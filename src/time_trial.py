from math import floor, ceil
from jinja2 import Environment, FileSystemLoader
from openpyxl import load_workbook


class TimeTrial:

    template_loader = False
    template_env = False

    def __init__(self, cols):
        self.cols = cols

        self.template_loader = FileSystemLoader(searchpath="templates/")
        self.template_env = Environment(loader=self.template_loader)
        self.template_env.trim_blocks = True
        self.template_env.lstrip_blocks = True

    def create_html(self, filename, delimiter):
        data = []

        # cell headers
        width1 = floor((100 * 4/5) // self.cols)
        width2 = floor((100 * 1/5) // self.cols)
        header = {'width_name': width1, 'width_time': width2}

        f = open(filename, 'r')
        lines = f.readlines()

        num_lines = len(lines)
        diff = int(ceil(num_lines/self.cols))
        # split into columns
        columns = []
        for x in range(0, self.cols):
            start = x * diff
            end = (x+1) * diff
            columns.append(lines[start:end])
            
        parse_format = 'new'
          
        if parse_format == 'new':
            for x in range(0, diff):
                row = []
                for y in range(0, len(columns)):
                    if x < len(columns[y]):
                        split = columns[y][x].split(delimiter)
                        name = split[0].strip()
                        result = split[1].replace('\n', '')
                        pb = split[2]
                        desc = split[3]
                        # print(desc)
                        # handle different ways of showing PB or first TT
                        if "**" in desc:
                            result_type = 'first'
                        elif "*" in desc:
                            result_type = 'pb'
                        else:
                            result_type = 'normal'
                        row.append({'name': name, 'time': {'result': result, 'result_type': result_type, 'prev': pb}})
                    else:
                        row.append({'name': '', 'time': {'result': '', 'result_type': 'none', 'prev': ''}})

                data.append(row)
        else:
            for x in range(0, diff):
                row = []
                for y in range(0, len(columns)):
                    if x < len(columns[y]):
                        split = columns[y][x].split(delimiter)
                        name = columns[y][x].rsplit(delimiter, 1)[0].strip()
                        score = split[len(split)-1]
                        score = score.replace('\n', '')
                        pb = ''
                        # handle different ways of showing PB or first TT
                        if "**" in score:
                            result_type = 'first'
                            result = score.replace("**", "")
                        elif "*" in score:
                            result_type = 'pb'
                            result = score
                        elif " PB" in score:
                            result_type = 'pb'
                            result = score.replace(" PB", "*")
                        elif "PB" in score:
                            result_type = 'pb'
                            result = score.replace("PB", "*")
                        else:
                            result_type = 'normal'
                            result = score

                        row.append({'name': name, 'time': {'result': result, 'result_type': result_type, 'prev': pb}})
                    else:
                        row.append({'name': '', 'time': {'result': '', 'result_type': 'none', 'prev': ''}})
                data.append(row)

        template = self.template_env.get_template("results.html")
        return template.render({'cols': self.cols, 'header': header, 'data': data})


class TimeTrialAnalysis:

    wb = False

    def __init__(self):
        self.wb = load_workbook('Run Monash Time Trial.xlsm')

    def print_details(self):
        print(self.wb.sheetnames)

        sheet = self.wb['Names']
        print("Max row: " + str(sheet.max_row))
        print("Max column: " + str(sheet.max_column))
