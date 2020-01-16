import subprocess
import os
import pwd
import logging


class Zone:
    """
    需要配置 rndc 配置 /etc/rndc.conf
    key "rndc-key" {
    algorithm hmac-md5;
    secret "h/NHws6RgIeZhS4p186XSg==";
    };

    options {
        default-key "rndc-key";
        default-server 127.0.0.1;
        default-port 953;
    };
    """

    def __init__(self, zone_template, config="/etc/rndc.key", data_root="/var/named"):
        self.command = "/usr/sbin/rndc"
        self.config = config
        self.data_root = data_root
        self.zone_template = zone_template

    @staticmethod
    def __command(command):
        result = subprocess.getstatusoutput(command)
        if result[0] == 0:
            return True
        else:
            logging.error(result)
            return False

    def make_command(self, action, zone, views, args=None):
        if args is None:
            command = "{rndc} -c {config} {action} {zone} in {views}"
        else:
            command = "{rndc}  -c {config} {action} {zone} in {views} '{args}'"
        return command.format(rndc=self.command, action=action, zone=zone, views=views, args=args, config=self.config)

    def add_zone(self, view, zone, file, args):
        command = self.make_command(action="addzone", views=view, zone=zone, args=args)
        if self.__create_zone_file(file=file):
            return self.__command(command)
        return False

    def __create_zone_file(self, file):
        zone_file = os.path.join(self.data_root, file)
        if os.path.exists(zone_file) and os.path.isfile(zone_file):
            return True
        try:
            with open(self.zone_template) as f:
                data = f.read()
            with open(zone_file, "w") as f:
                f.write("{data}\n".format(data=data))
            user_info = pwd.getpwnam("named")
            os.chown(zone_file, user_info.pw_uid, user_info.pw_gid)
            return True
        except FileNotFoundError as e:
            logging.error("zone file create fail please manual create {err}".format(err=e))
        return False

    def __remove_zone_file(self, file):
        zone_file = os.path.join(self.data_root, file)
        try:
            os.remove(zone_file)
            return True
        except FileNotFoundError as e:
            logging.error("zone file remove fail please manual remove {err}".format(err=e))
            return False

    def del_zone(self, view, zone, file, is_delete_file=False):
        command = self.make_command(action="delzone", views=view, zone=zone)
        if self.__command(command):
            if is_delete_file:
                self.__remove_zone_file(file=file)
            return True
        return False


# if __name__ == '__main__':
#     zone_template = "/tmp/pycharm_project_682/agent/conf/default_template_zone.zone"
#     a = Zone(zone_template)
#     print(a.add_zone("shanghai", "xiaoxin.cc", "xiaoxin.cc.zone", '{type master; file "xiaoxin.cc.zone"; allow-update {key golet;};};'))
#     a.del_zone("beijing", "xiaoxin.cc", "xiaoxin.cc.zone")
    # a.create_zone_file("dasda")
    # a.del_zone("beijing", "dasda", "")
    # a = Zone()
    # print(a.make_command("addzone", "xiaoxin.cc", "beijing"))
    # a.add_zone()
