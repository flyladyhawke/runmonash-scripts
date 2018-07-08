from __future__ import division
import os
import math

class TimeTrialTemplate:

    legend = '''
<p><span style="color:green">Time in green is a PB</span><br/>
<span style="color:blue">Time in blue is a first Time Trial</span></p>
'''

    table_start = '''
<table style="color:black;width:90%;border:1px solid black;border-collapse:collapse">
<tbody>
'''
    table_end = '''
</tbody>
</table>
'''
        
    table_header_cell_template = '<th style="width:{}%;border-bottom:1px solid black;padding-left:5px">Name</th><th style="width:{}%;border-right:1px solid black;border-bottom:1px solid black">Time</th>'
    table_tbody_cell_template = '<td style="border-bottom:1px dotted black;padding-left:5px">{}</td><td style="border-right:1px solid black;border-bottom:1px dotted black">{}</td>'
    
    score_pb_template = '<span title="Prev PB - {}" style="color:green;">{}*</span>'
    score_curr_template = '<span title="Curr PB - {}">{}</span>'
    score_new_template = '<span style="color:blue;">{}</span>'
    

class TimeTrial:

    def __init__(self, cols):
        self.cols = cols
        self.template = TimeTrialTemplate()
    
    def createHtml(self, filename, delimiter):               
        text  = self.template.legend
        text += self.template.table_start

        # cell headers
        text += '<tr>\n'
        width1 = math.floor((100 * 4/5) // self.cols)
        width2 = math.floor((100 * 1/5) // self.cols)
        for x in range(0, self.cols):
            text += self.template.table_header_cell_template.format(width1, width2)
        text += '</tr>\n'

        f = open(filename, 'r')
        lines = f.readlines()

        num_lines = len(lines)
        diff = math.ceil(num_lines/self.cols)
        # split into columns
        columns = []
        for x in range(0, self.cols):
            start = x * diff
            end = (x+1) * diff
            columns.append(lines[start:end]); 
            
        parseformat = 'new';    
          
        if (parseformat == 'new'):    
            for x in range(0, diff):
                text += '<tr>\n'
                for y in range(0, len(columns)):
                    if x < len(columns[y]) :
                        split = columns[y][x].split(delimiter)
                        name =  split[0].strip()
                        score = split[len(split)-3]
                        pb = split[len(split)-2]
                        score = score.replace('\n','')
                        desc = split[len(split)-1]
                        # print(desc)
                        # handle different ways of showing PB or first TT
                        if "**" in desc:
                            score = self.template.score_new_template.format(score)
                        elif "*" in desc:
                            score = self.template.score_pb_template.format(pb, score)
                        else:
                            score = self.template.score_curr_template.format(pb, score)
                           
                        text += self.template.table_tbody_cell_template.format(name, score)
                    else:
                        text += self.template.table_tbody_cell_template.format('', '')
                text += '</tr>\n'                  
        else:
            for x in range(0, diff):
                text += '<tr>\n'
                for y in range(0, len(columns)):
                    if x < len(columns[y]) :
                        split = columns[y][x].split(delimiter)
                        name =  columns[y][x].rsplit(delimiter, 1)[0].strip()
                        score = split[len(split)-1]
                        score = score.replace('\n','')
                        # handle different ways of showing PB or first TT
                        if "**" in score:
                            score = '<span style="color:blue;">'+score.replace("**", "")+'</span>'
                        elif "*" in score:
                            score = '<span style="color:green;">'+score+'</span>'
                        elif " PB" in score:
                            score = '<span style="color:green;">'+score.replace(" PB", "*")+'</span>'
                        elif "PB" in score:    
                            score = '<span style="color:green;">'+score.replace("PB", "*")+'</span>'

                        text += self.template.table_tbody_cell_template(name, score)
                    else:
                        text += self.template.table_tbody_cell_template('', '')
                text += '</tr>\n'

        text += self.template.table_end
        text += '\n\n\n\n\n'  
        return text    