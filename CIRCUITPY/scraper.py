import adafruit_requests
import re
import ssl
import wifi
import socketpool

class Scraper:
    WORKOUT_URL = "https://www.concept2.com/indoor-rowers/training/wod/workout/nojs/today"
    ALT_WORK_URL = "https://www.concept2.com/indoor-rowers/training/wod/workout/nojs/random"
    URL_ENDS = {'short':'/short/rower', 'medium':'/medium/rower', 'long':'/long/rower'}
    
    #circuitpython does not support beautiful soup or other html parsers :(
    REGEX_TXT = r'<section id="wod-.*?<h4>([^<]+).*?<p class="light">([^<]+).*?<strong>.*?PM5.*?<\/strong>: ([^<]+)'

    def __init__(self):
        self.workouts = {'short': {'title': None, 'body': None, 'pm5': None},
                         'alt_short': {'title': None, 'body': None, 'pm5': None},
                         'medium': {'title': None, 'body': None, 'pm5': None},
                         'alt_medium': {'title': None, 'body': None, 'pm5': None},
                         'long': {'title': None, 'body': None, 'pm5': None},
                         'alt_long': {'title': None, 'body': None, 'pm5': None}}
        self.regex = re.compile(self.REGEX_TXT)
        self.pool = socketpool.SocketPool(wifi.radio)
        self.requests = adafruit_requests.Session(self.pool, ssl.create_default_context())

    
    def get_workouts(self):
        return self.workouts

    def get_workout(self, key):
        if key in self.workouts.keys():
            return (key, self.workouts[key])
        else:
            return None
    
    def get_alts(self):
        alts = {}
        for key in self.endings.keys():
            alts["alt_"+key] = self.workouts["alt_"+key]
        return alts

    def scrape(self):
        workouts = {}
        for key, url in self.URL_ENDS.items():
            #Main Workout of Day
            response = self.requests.get(self.WORKOUT_URL+url)
            html_text = self._remove_lines(response.text)
            print(html_text+'\n-------\n')
            html_text = self._declutter_text(html_text)
            print(html_text)
            match = self.regex.search(html_text)
            #Create Dictionary of mains
            wo_dict = {}
            wo_dict['title'] = match.group(1).strip()
            wo_dict['body'] = match.group(2).strip()
            wo_dict['pm5'] = self._condense(match.group(3).strip())
            #Alt Workout of Day
            alt_response = self.requests.get(self.ALT_WORK_URL+url)
            alt_html_text = self._remove_lines(alt_response.text)
            alt_html_text = self._declutter_text(alt_html_text)
            alt_match = self.regex.search(alt_html_text)
            #Create Dictionary of Alts
            alt_dict = {}
            alt_dict['title'] = alt_match.group(1).strip()
            alt_dict['body'] = alt_match.group(2).strip()
            alt_dict['pm5'] = self._condense(alt_match.group(3).strip())
            workouts[key] = wo_dict
            workouts['alt_'+key] = alt_dict
        self.workouts = workouts
        return workouts
    

    def new_alts(self):
        workouts = {}
        for key, url in self.URL_ENDS.items():
            alt_resp = self.requests.get(self.ALT_WORK_URL+url)
            alt_text = self._remove_lines(alt_resp)
            alt_text = self._declutter_text(alt_text)
            alt_match = self.regex.search(alt_text)
            alt_dict = {}
            alt_dict['title'] = alt_match.group(1).strip()
            alt_dict['body'] = alt_match.group(2).strip()
            alt_dict['pm5'] = self._condense(alt_match.group(3).strip())
            workouts['alt_'+key] = alt_dict
            self.workouts['alt_'+key] = alt_dict
        return workouts

    def scrape_no_re(self):
        workouts = {}
        for key, url in self.URL_ENDS.items():
            #Main Workout of Day
            response = self.requests.get(self.WORKOUT_URL+url)
            html_text = self._remove_lines(response.text)
            #print(html_text+'\n-------\n')
            html_text = self._declutter_text(html_text)
            #print(html_text)
            title = html_text.split("<h4>")[1].split("</h4>")[0]
            body = html_text.split('<p class="light">')[1].split("</p>")[0]
            buttons = html_text.split("PM5</strong>:")[1].split("</p>")[0]
            #Create Dictionary of mains
            wo_dict = {}
            wo_dict['title'] = title.strip()
            wo_dict['body'] = body.strip()
            wo_dict['pm5'] = self._condense(buttons.strip())
            #Alt Workout of Day
            alt_response = self.requests.get(self.ALT_WORK_URL+url)
            alt_html_text = self._remove_lines(alt_response.text)
            alt_html_text = self._declutter_text(alt_html_text)
            alt_title = alt_html_text.split("<h4>")[1].split("</h4>")[0]
            alt_body = alt_html_text.split('<p class="light">')[1].split("</p>")[0]
            alt_buttons = alt_html_text.split("PM5</strong>:")[1].split("</p>")[0]
            #Create Dictionary of Alts
            alt_dict = {}
            alt_dict['title'] = alt_title.strip()
            alt_dict['body'] = alt_body.strip()
            alt_dict['pm5'] = self._condense(alt_buttons.strip())
            workouts[key] = wo_dict
            workouts['alt_'+key] = alt_dict
        self.workouts = workouts
        print(workouts)
        return workouts

    def debug(self):
        self.workouts = {}
        workouts = {'short': {'title': "6 x 500m / 1 min easy", 
                              'body': "Row six 500 meter pieces. Row for one minute at light pressure between each 500.", 
                              'pm5': "B-A-E"},
                    'alt_short': {'title': "5 x 500m / 1 min easy", 
                                  'body': "Row 5 500 meter pieces. Row for one minute at light pressure between each 500.", 
                                  'pm5': "B-A-E"},
                    'medium': {'title': "4 x 6 min / 2 min easy", 
                               'body': "Row four 6 minute pieces. Row for two minutes at light pressure between each piece.", 
                               'pm5': "B-2D-6B-4A-2B-E"},
                    'alt_medium': {'title': "4 x 5 min / 2 min easy", 
                                   'body': "Row four 5 minute pieces. Row for two minutes at light pressure between each piece.", 
                                   'pm5': "B-2D-6B-4A-2B-E"},
                    'long': {'title': "2 x 6000m / 6 min easy", 
                             'body': "Row two 6000 meter pieces. Row for six minutes at light pressure between each piece", 
                             'pm5': "B-2D-A-D-6B-A-5C-4A-6B-E"},
                    'alt_long': {'title': "2 x 6020m / 6 min easy", 
                                 'body': "Row two 6020 meter pieces. Row for six minutes at light pressure between each piece", 
                                 'pm5': "B-2D-A-D-6B-A-5C-4A-6B-E"}}
        self.workouts = workouts
        return workouts

    #Button press condensing:

    def _condense(self, text):
        buttons = text.split('-')
        buttons = self._condense_singles(buttons)
        buttons = self._duplicate_pattern(buttons, 2)
        button_string = '-'.join(buttons)
        return button_string

    
    def _condense_singles(self, list_of_char):
        i = 0
        while i < len(list_of_char):
            j = i+1
            count = 1
            while j < len(list_of_char):
                if list_of_char[i] == list_of_char[j]:
                    count += 1
                    j += 1
                else:
                    break
            if count > 1:
                list_of_char[i] = str(count)+list_of_char[i]
                for k in range(count-1):
                    list_of_char.pop(i+1)
            i += 1
        return list_of_char

    
    def _duplicate_pattern(self, listchar, pattern_size):
        i = 0
        while i+pattern_size <= len(listchar):
            count = 1
            j = i+pattern_size
            while j < len(listchar):
                if listchar[i:i+pattern_size] == listchar[j:j+pattern_size]:
                    count += 1
                    j += pattern_size
                else:
                    break
            if count > 1:
                listchar[i] = str(count)+''.join(listchar[i:i+pattern_size])
                for k in range((count*pattern_size)-1):
                    listchar.pop(i+1)
            i += 1
        return listchar


# Helpers for non-Regex scraping:

    def _declutter_text(self, text):
        front_split = text.split("main-content")[1]
        final = front_split.split("global container")[0]
        return final

    def _remove_lines(self, text):
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        return text
