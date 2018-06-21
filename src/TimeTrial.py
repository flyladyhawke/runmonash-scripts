from __future__ import division
import os
import math

class TimeTrial:
    
    def createHtml(self, filename, delimiter, cols):
        f = open(filename, 'r')
        
        text  = '<p><span style="color:green">Time in green is a PB</span><br/>\n'
        text += '<span style="color:blue">Time in blue is a first Time Trial</span></p>\n'
        text += '<table style="color:black;width:90%;border:1px solid black;border-collapse:collapse">\n'
        text += '<tbody>'

        # cell headers
        text += '<tr>\n'
        for x in range(0, cols):
            text  += '<th style="width:'+str(math.floor(100/cols * 4/5))+'%;border-bottom:1px solid black;padding-left:5px"> Name</th>\n'
            text  += '<th style="width:'+str(math.floor(100/cols * 1/5))+'%;border-right:1px solid black;border-bottom:1px solid black"> Time</th>\n'
        text += '</tr>\n'

        lines = []
        for line in f:
            lines.append(line)

        num_lines = len(lines)
        diff = int(math.ceil(num_lines/cols))
        # split into columns
        columns = []
        for x in range(0, cols):
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
                            score = '<span style="color:blue;">'+score+'</span>'
                        elif "*" in desc:
                            score = '<span title="Prev PB - '+pb+'" style="color:green;">'+score+"*"'</span>'
                        else:
                            score = '<span title="Curr PB - '+pb+'">'+score+'</span>'
                            
                        text += '<td style="border-bottom:1px dotted black;padding-left:5px">'+name+'</td>\n'
                        text += '<td style="border-right:1px solid black;border-bottom:1px dotted black">'+score+'</td>\n'
                    else:
                        text += '<td style="border-bottom:1px dotted black;padding-left:5px"> </td>\n'
                        text += '<td style="border-right:1px solid black;border-bottom:1px dotted black"> </td>\n'
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

                        text += '<td style="border-bottom:1px dotted black;padding-left:5px">'+name+'</td>\n'
                        text += '<td style="border-right:1px solid black;border-bottom:1px dotted black">'+score+'</td>\n'
                    else:
                        text += '<td style="border-bottom:1px dotted black;padding-left:5px"> </td>\n'
                        text += '<td style="border-right:1px solid black;border-bottom:1px dotted black"> </td>\n'
                text += '</tr>\n'

        text += '</tbody>'
        text += '</table>'
        text += '\n\n\n\n\n'  
        return text    