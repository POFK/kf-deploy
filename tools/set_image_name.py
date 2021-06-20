import os
import yaml
import json
import pprint
from datetime import date

class Node(object):

    def __init__(self, name):
        self.name = name

    def __str__(self, level=0):
        log = "<Node {}>".format(self.name)
        return log

    def __repr__(self):
        return self.__str__()

class TreeNode(Node):

    def __init__(self, conf_path='', base=None, over=None):
        name = self.hash_node_name(conf_path)
        self.base = []
        self.over = []
        self.images = {}
        self.path = conf_path
        if base:
            self.add_base(base)
        if over:
            self.add_over(over)
        super(TreeNode, self).__init__(name)

    def __str__(self, level=0):
        ret = "-->\t"*level+repr(self.name)+"\n"
        for base in self.base:
            ret += base.__str__(level+1)
        return ret

    def hash_node_name(self, path):
        return str(abs(hash(path)) % (10 ** 8))

    def add_base(self, obj=None):
        if obj is None:
            raise ValueError('please input obj name or treenode')
        elif obj and not isinstance(obj, TreeNode):
            obj = TreeNode(obj)
        if obj not in self.base:
            self.base.append(obj)
        if self not in obj.over:
            obj.add_over(self)

    def add_over(self, obj=None):
        if obj is None:
            raise ValueError('please input obj name or treenode')
        elif obj and not isinstance(obj, TreeNode):
            obj = TreeNode(obj)
        if obj not in self.over:
            self.over.append(obj)
        if self not in obj.base:
            obj.add_base(self)


class KustomizeTools(object):
    def __init__(self, basedir=''):
        self.basedir = basedir
        self.root = TreeNode(conf_path=basedir)
        self.root.resources = [self.root.path]

    def collect_base_images(self, obj):
        for base in obj.base:
            obj.images = {**obj.images, **self.collect_base_images(base)}
        return obj.images

    def is_conf_file(self, fname):
        return "kustomization.yaml" in fname

    def add_conf_suffix(self, fname):
        return os.path.join(fname, "kustomization.yaml")

    def writeconfig(self, file, data):
        with open(file, 'w') as fp:
            yaml.dump(data, fp)

    def checkimageupdate(self, data):
        return "images" in data

    def findfiles(self, basedir):
        listOfFiles = []
        for (dirpath, dirnames, filenames) in os.walk(basedir):
            for file in filenames:
                if self.is_conf_file(file):
                    listOfFiles.append({"dir": dirpath, "file": file})
        return listOfFiles

    def loadconfig(self, file):
        if not self.is_conf_file(file):
            file = self.add_conf_suffix(file)
        with open(file, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return data

    def get_base_resources(self, file, over_node):
        fp = os.path.join(file['dir'],file['file'])
        data = self.loadconfig(fp)
        node = TreeNode(fp)
        over_node.add_base(node)
        base_resources = [os.path.join(file["dir"], res) for res in data["resources"]]
        if "bases" in data:
            base_resources += [os.path.join(file["dir"], res) for res in data["bases"]]
        node.resources = base_resources
        if self.checkimageupdate(data) and node.over[0] is not self.root:
            node.images = {fp: data['images']}
        return node

    def create_ktree(self, node):
        """
        usage: self.create_ktree(self.root)
        """
        for res in node.resources:
            base_files = self.findfiles(res)
            for fp in base_files:
                base_node = self.get_base_resources(fp, node)
                self.create_ktree(base_node)

class SetImage(KustomizeTools):

    def __init__(self, is_write=False, **kwargs):
        self.pre = "docker.io/txmao/kf12-"
        self.today_tag = date.today().strftime("%Y%m%d")
        self.is_write = is_write
        super(SetImage, self).__init__(**kwargs)

    def __call__(self):
        self.create_ktree(self.root)
        self.collect_base_images(self.root)
        self.images = []
        for node in self.root.base:
            if len(node.images) == 0:
                continue
            data = self.loadconfig(node.path)
            images = sum(list(node.images.values()), [])
            images = [self.parse_image(im) for im in images]
            self.save_updated_images_in_config(node.path, images, data)
            self.images += images
        self.create_action_matrix()

    def parse_image(self, image):
        if "digest" in image:
            image["tag"] = image["digest"]
            image["newTag"] = image["digest"]
            image["newTag"] = image["newTag"].split(":")[-1][:10]
            sp = "@"
        else:
            image["tag"] = image["newTag"]
            if image["newTag"] == "latest":
                image["newTag"] = self.today_tag
            sp = ":"
        pre=""
        if "/" not in image["name"]:
            pre="library/"+pre
        if ".io" not in image["name"].split("/")[0]:
            pre="docker.io/"+pre
        image["pull"] = "{}{}{}{}".format(pre,image["name"],sp,image["tag"])
        image["newName"] = self.pre+image["name"].replace("/",".")
        image["push"] = "{}{}{}".format(image["newName"],":",image["newTag"])
        return image

    def create_action_matrix(self):
        images = self.images
        self.remove_image_with_env(images)
        images = self.remove_repeat_items(images)
        self.matrix_data = {"include": [{"src": i["pull"], "dst": i["push"], "experimental":True} for i in images] }

    def matrix_output(self):
        print(json.dumps(self.matrix_data).replace(" ",""))


    def save_updated_images_in_config(self, fp, parsed_images, data):
        data["images"] = [{k: im[k] for k in ("name", "newTag", "newName")} for im in parsed_images]
        # check image changes
#       print(fp, len(data["images"]))
        # check image changes
        if not self.is_write:
            return 0
        self.writeconfig(fp, data)

    def check_env_params(self, images, fp):
        for image in images:
            if "$(" in image["name"]:
                print(fp)
                break

    def remove_image_with_env(self, images):
        """ FIXIT: those images with env should be tag and push to docker hub manually."""
        remove = []
        for im in images:
            if "$(" in im["name"]:
                remove.append(im)
        for im in remove:
            images.remove(im)

    def remove_repeat_items(self, images):
        srclist = []
        newimages = []
        for im in images:
            src = im["name"]+im["tag"]
            if src in srclist:
                continue
            srclist.append(src)
            newimages.append(im)
        return newimages


if __name__ == '__main__':
    # usage: python set_image_name.py --dry-run
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true')
    args = parser.parse_args()
    import pprint

    si = SetImage(basedir="/config/workspace/learnk8s/kubeflow/kf-test/kustomize", is_write=not args.dry_run)
    si()
    si.matrix_output()

#   pprint.pprint(si.matrix_data)
