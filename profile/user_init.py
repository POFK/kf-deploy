#!/usr/bin/env python3
import os
import yaml

res_dict = {
    "small": {"cpu":"12.5", "memory":"64Gi", "requests.nvidia.com/gpu":"1", "persistentvolumeclaims":"5", "requests.storage":"100Gi"},
    "mid": {"cpu":"24.5", "memory":"128Gi", "requests.nvidia.com/gpu":"2", "persistentvolumeclaims":"5", "requests.storage":"500Gi"},
    "big": {"cpu":"32.5", "memory":"250Gi", "requests.nvidia.com/gpu":"4", "persistentvolumeclaims":"5", "requests.storage":"1Ti"},
}

class User(object):
    def __init__(self, user, email, resource_level):
        self.user = user
        self.email = email
        self.rl = resource_level
        self.user_pref = "user-"
        self.profile = None
        self.pv = None
        self.pvc = None


    def __str__(self):
        text = "---\n"
        if self.profile:
            text += yaml.dump(self.profile)
            text += "---\n"
        if self.pv:
            text += yaml.dump(self.pv)
            text += "---\n"
            text += yaml.dump(self.pvc)
        return text

    def loadconfig(self, file):
        with open(file, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return data

    def writeconfig(self, file, data):
        with open(file, 'w') as fp:
            yaml.dump(data, fp)

    def gen_profile(self):
        self.profile = self.loadconfig("profile-temp.yaml")
        self.profile['spec']['resourceQuotaSpec'] = res_dict[self.rl]
        self.profile['metadata']['name'] = self.user_pref + self.user
        self.profile['spec']['owner']['name'] = "/user/"+self.email

    def gen_pvc(self):
        self.pvc = self.loadconfig("data-vol-pvc.yaml")
        self.pvc['metadata']['namespace'] = self.user_pref + self.user
        self.pvc['spec']['selector']["matchLabels"]["user"] = self.user_pref + self.user

    def gen_pv(self):
        self.pv = self.loadconfig("data-vol-pv.yaml")
        self.pv['metadata']['name'] = "inspur-disk01-" + self.user
        self.pv['metadata']['labels']["user"] = self.user_pref + self.user
        self.pv['spec']['nfs']["path"] = os.path.join(self.pv['spec']['nfs']["path"], self.user)

    def gen(self, mode):
        if mode == "all" or mode == "pv":
            self.gen_pvc()
            self.gen_pv()
        if mode == "all" or mode == "profile":
            self.gen_profile()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str, help='User name')
    parser.add_argument('--email', type=str, help='User email')
    parser.add_argument('--level', type=str, choices=['small', 'mid', 'big'],help='Resources level')
    parser.add_argument('--mode', type=str, default="all", choices=['all', 'pv', 'profile'],help='generate pv, profile or all of them')
    args = parser.parse_args()
    u = User(args.user,args.email,args.level)
    u.gen(mode=args.mode)
    print(u)
