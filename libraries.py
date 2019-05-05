import os
import uuid
import shutil


class envparser:

    @classmethod
    def parse(cls, content):
        lines = content.splitlines()

        envs = {}
        for line in lines:
            keyval = line.split('=', 1)

            if len(keyval) is not 2:
                continue

            envs[keyval[0]] = keyval[1]

        return envs

    @classmethod
    def parse_file(cls, file_path):
        if not os.path.exists(file_path):
                raise Exception("Unable to locate %s environment file" % file_path)

        file = open(file_path)
        content = file.read()
        file.close()

        envs = cls.parse(content)

        return envs

    @classmethod
    def update_parameters_in_file(cls, file_path, parameters={}):
        if not os.path.exists(file_path):
                raise Exception("Unable to locate %s environment file" % file_path)

        random_filename = str(uuid.uuid4()) + '.temp'

        file = open(file_path)
        content = file.read()
        file.close()

        lines = content.splitlines()

        envlines = []
        for line in lines:
            keyval = line.split('=', 1)

            if len(keyval) is 2:
                if keyval[0] in parameters:
                    keyval[1] = parameters[keyval[0]]

                envlines.append('%s=%s' % (keyval[0], keyval[1]))
            else:
                envlines.append(line)

        out_filepath = "./%s" % (random_filename)
        out_temp_file = open(out_filepath, "w")
        for line in envlines:
            # write line to output file
            out_temp_file.write(line)
            out_temp_file.write("\n")
        out_temp_file.close()

        # now override original file
        shutil.move(out_filepath, file_path)


class template:

    @classmethod
    def parse(cls, template, parameters):
        path = 'templates/%s.tpl' % (template,)

        if not os.path.exists(path):
            raise Exception("Unable to find template: %s" % path)

        file = open(path)
        content = file.read()
        file.close()

        return content
