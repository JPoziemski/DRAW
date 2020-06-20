from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import subprocess

# Test to run needs a running instance of gui_app.py
# Test GUI in Chrome:91 for linux 64

chromedriver_path = './chromedriver'
chromedriver = webdriver.Chrome(chromedriver_path)
chromedriver.get('http://127.0.0.1:2000/index')

# Test index.html
chromedriver.find_element_by_css_selector('.button').click()

# Test generate.html
select = Select(chromedriver.find_element_by_id('run_type'))
select.select_by_value('complete_analysis')
time.sleep(2)

select = Select(chromedriver.find_element_by_id('seq_type'))
select.select_by_value('paired_end')
time.sleep(2)

inputElement = chromedriver.find_element_by_id("annotation_file_name")
inputElement.send_keys('Homo_sapiens.GRCh38.100.chromosome.22.gff3')
time.sleep(2)

inputElement = chromedriver.find_element_by_id("reference_file_name")
inputElement.send_keys('Homo_sapiens.GRCh38.dna.chromosome.22.fa')
time.sleep(2)

inputElement = chromedriver.find_element_by_id("input_file_prefix")
inputElement.send_keys('HBR')
time.sleep(2)

inputElement = chromedriver.find_element_by_id("control_file_prefix")
inputElement.send_keys('seq_control')
time.sleep(2)

inputElement = chromedriver.find_element_by_id("threads_number")
inputElement.send_keys('4')
time.sleep(2)

chromedriver.find_element_by_id('run_downstream_analysis').click()
time.sleep(2)

chromedriver.find_element_by_xpath("//form[input/@type='submit']").submit()
time.sleep(2)

# Test tools / complete_analysis.html
select = Select(chromedriver.find_element_by_name('tool_INITIAL_QUALITY_CONTROL'))
select.select_by_value('FastQC_0')
inputElement = chromedriver.find_element_by_name("FastQC_0_param!--min_length")
inputElement.send_keys('10')
inputElement = chromedriver.find_element_by_name("FastQC_0_param!--kmers")
inputElement.send_keys('4')
chromedriver.find_element_by_name('FastQC_0_param!--nogroup').click()
time.sleep(2)

select = Select(chromedriver.find_element_by_name('tool_TRIMMING'))
select.select_by_value('TRIMMOMATIC')
inputElement = chromedriver.find_element_by_name("TRIMMOMATIC_param!ILLUMINACLIP")
inputElement.send_keys('TruSeq3-PE:2:30:10')
inputElement = chromedriver.find_element_by_name("TRIMMOMATIC_param!SLIDINGWINDOW")
inputElement.send_keys('4:15')
inputElement = chromedriver.find_element_by_name("TRIMMOMATIC_param!LEADING")
inputElement.send_keys('3')
inputElement = chromedriver.find_element_by_name("TRIMMOMATIC_param!TRAILING")
inputElement.send_keys('3')
inputElement = chromedriver.find_element_by_name("TRIMMOMATIC_param!MINLEN")
inputElement.send_keys('36')
time.sleep(2)

select = Select(chromedriver.find_element_by_name('tool_AFTER_TRIMMING_CONTROL'))
select.select_by_value('FastQC_1')
inputElement = chromedriver.find_element_by_name("FastQC_1_param!--min_length")
inputElement.send_keys('10')
inputElement = chromedriver.find_element_by_name("FastQC_1_param!--kmers")
inputElement.send_keys('6')
chromedriver.find_element_by_name('FastQC_1_param!--nogroup').click()
time.sleep(2)

select = Select(chromedriver.find_element_by_name('tool_MAPPING'))
select.select_by_value('Hisat2')
inputElement = chromedriver.find_element_by_name("hisat_param!--mp")
inputElement.send_keys('10')
time.sleep(2)

select = Select(chromedriver.find_element_by_name('tool_COUNTING'))
select.select_by_value('Stringtie')
time.sleep(2)

chromedriver.find_element_by_xpath("//input[@type='submit']").submit()


# Test overview.html
chromedriver.find_element_by_xpath("//input[@type='submit']").click()

print(chromedriver.title)
chromedriver.close()