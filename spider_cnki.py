# coding = utf-8
import requests
import jieba
import jieba.analyse
import re
from bs4 import BeautifulSoup
# from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pymysql.cursors

times = 3

url_arry = {
    'domain' : 'http://www.cnki.net',
    'kcms' : 'kcms',
    'detail' : 'detail',
    'frame' : 'frame',
    'detailfile' : 'detail.aspx',
    'listfile' : 'detaillist.aspx'
}

reftype = {
    'reference' : 1,
    'similarity' : 7,
    'focus' : 8
}

htmldom = {
    'titleid' : 'chTitle',
    'entitleid' : 'entitle',
    'authorclass' : 'KnowledgeNetLink',
    'abstractid' : 'ChDivSummary',
    'keywordid' : 'ChDivKeyWord',
    'listvid' : 'listv',
    'zwjdown' : 'zwjdown',
    'zwjRightRow' : 'zwjRightRow',
    'entable' : 'table[bgcolor=#f1f1f1]',
    'strContext' : 'strContext',
    'filenameid' : 'filename',
    'tablenameid' : 'tablename'
}

def get_text_by_id(soup, id_string):
    elem = soup.find(id=id_string)
    if elem != None:
        return elem.get_text()
    else :
        return ''

def create_html(url):
    r = requests.get(url)
    return r.text

def run_article_list(url, aricle_from, run_times):
    print url
    list_html_code = create_html(url)
    list_soup = BeautifulSoup(list_html_code, 'html.parser')
    list_li = list_soup.find_all('li')
    for li in list_li:
        list_a = li.find('a')
        if list_a != None:
            if list_a.has_attr('href'):
                run_article(url_arry['domain']+list_a['href'], aricle_from, run_times)
                # print list_a['href']
            else:
                print list_a.get_text()
        else:
            lp = re.compile('\s+')
            li_text = re.sub(lp, '', li.get_text())
            print li_text
    # print list_li

def run_article(url, aricle_from, run_times):
    if run_times is 0:
        return 0

    print run_times

    html_code = create_html(url)
    soup = BeautifulSoup(html_code, 'html.parser')

    article_title = soup.find(id=htmldom['titleid'])

    if article_title != None:
        title = article_title.get_text()

        abstract = get_text_by_id(soup, htmldom['abstractid'])

        print title

        print abstract
        ################
        keywords = get_text_by_id(soup, htmldom['keywordid'])
        p = re.compile('\s+')
        keywords = re.sub(p, '', keywords)
        # seg_list = jieba.cut(abstract, cut_all=False)

        print keywords
        ################
        # if(mysql_query('insert ignore into `articles` (`title`, `author`, `abstract`, `keywords`, `filename`, `dbcode`, `type`, `href`, `toname`) values ("'.$article_information['title'].'", "'.$article_information['author'].'", "'.$article_information['abstract'].'", "'.$article_information['keywords'].'", "'.$article_information['filename'].'", "'.$article_information['dbcode'].'", "'.'1'.'", "'.html_encode($urllist).'", "'.$from.'");'))
        #     echo "<a href=".$urllist.">".$article_information['title']."</a> <strong>".$times."</strong> \n";
        # else echo(mysql_error());

        ################
        listv = soup.find(id=htmldom['listvid'])['value']
        zwjdown_string = soup.find('div', {'class': htmldom['zwjdown']}).a['href'].strip()

        pm = re.compile('filename=([^&]+)&dbcode=([^&]+)&dbname=([^&]+)')
        match = re.search(pm, zwjdown_string)
        if match:
            filename = match.group(1)
            dbcode = match.group(2)
            dbname = match.group(3)

        listurl = url_arry['domain'] + '/' + url_arry['kcms'] + '/' + url_arry['detail'] + '/' + url_arry['frame'] + '/' + url_arry['listfile'] + '?filename=' + filename + '&dbcode=' + dbcode + '&dbname=' + dbname + '&reftype=' + str(reftype['reference']) + '&vl=' + listv
        run_article_list(listurl, url, run_times-1)
        #################
        # print('/ '.join(seg_list))
        # for x, w in jieba.analyse.extract_tags(abstract, withWeight=True):
        #     print('%s %s' % (x, w))

        # wordcloud = WordCloud(max_font_size=40, relative_scaling=.5).generate(abstract)
        # plt.figure()
        # plt.imshow(wordcloud)
        # plt.axis('off')
        # plt.show()
        #################
    elif soup.find(id=htmldom['entitleid']) != None:
        article_title = soup.find(id=htmldom['entitleid'])
        en_title = article_title.get_text()
        print en_title
    else :
        return 0

def main():
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='forestry_literature', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    get_cur = conn.cursor()
	insert_cur = conn.cursor()
    # fd = open('in.txt', 'r')
    # for line in fd:
    #     print line.strip('\n')
    #     run_article(line.strip('\n'), 0, times)

    # run_article('', 0, times)
    article_url = 'http://www.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=cmfd201402&filename=1014327913.nh'
    run_article(article_url, 0, times)
    get_cur.close()
	insert_cur.close()
    conn.close()

if __name__ == '__main__':
    main()
