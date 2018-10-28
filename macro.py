from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import getpass

interpark_id = input('인터파크 아이디를 입력하세요 : ')
interpark_pw = getpass.getpass('인터파크 비밀번호를 입력하세요 : ')
interpark_game = input('예매하실 게임을 입력해주세요 (ex: 1) : ') + "차전"
interpark_seats = ['1루 의자지정석', '3루 의자지정석', '1루 응원지정석', '3루 응원지정석', '1루 휠체어장애인석', '3루 휠체어장애인석', '그린존', '일반석']
print("좌석 목록 : ")
for seat in interpark_seats:
    print(seat)
interpark_seat = input('우선 예약할 좌석명을 입력해주세요 : ')
interpark_ticket_count = input('예매할 티켓의 매수를 입력해주세요 (ex: 1) : ') + "매"
interpark_he_is_sick = False

if interpark_seat == "1루 휠체어장애인석" or interpark_seat == "3루 휠체어장애인석":
    interpark_he_is_sick = True
    he_is_sick = input("동반인과 함께 할 경우 1, 아닐 경우 2를 입력하고 엔터를 눌러주세요 : ")

interpark_this_game_available = False
interpark_this_captcha_available = False

driver = webdriver.Chrome('./chromedriver.exe')
driver.get('http://ticket.interpark.com/Ticket/Goods/GoodsInfo_KBO.asp')

# 인터파크 로그인
driver.find_element_by_id('aLogin').click()
driver.find_element_by_id('UID').send_keys(interpark_id)
driver.find_element_by_id('PWD').send_keys(interpark_pw)
driver.execute_script('login()')

start = input("예매를 시작하려면 엔터키를 눌러주세요")

# 예매
schedule = driver.find_elements_by_xpath("//ul[@class='schedule']/li")
for game in schedule:
    game_html = game.get_attribute('innerHTML')
    soup = BeautifulSoup(game_html, 'html.parser')
    game_name = soup.find('p', {'class' : 'gameRud'}).text
    if game_name == interpark_game:
        # 캡차 처리
        game_btn = soup.find('a')
        while not interpark_this_game_available:
            try:
                driver.execute_script(game_btn.get('onclick'))
                interpark_this_game_available = True
            except:
                driver.execute_script('window.location.reload()')
        driver.switch_to_window(driver.window_handles[1])
        driver.switch_to_frame(driver.find_element_by_id('ifrmSeat'))
        if driver.find_element_by_id('divRecaptcha').get_attribute('style') == 'display: none;':
            driver.execute_script('window.location.reload()')
        while not interpark_this_captcha_available:
            captcha = input('화면에 표시된 문자를 입력해주세요 : ')
            script = "document.getElementById('txtCaptcha').value = '" + captcha + "'"
            driver.execute_script(script)
            driver.execute_script('fnCheck()')
            if driver.find_element_by_id('divRecaptcha').get_attribute('style') == 'display: none;':
                interpark_this_captcha_available = True
        # 좌석 선택
        driver.switch_to_window(driver.window_handles[1])
        driver.switch_to_frame(driver.find_element_by_id('ifrmSeat'))
        seats = driver.find_elements_by_xpath("//div[@class='list']/a")
        # 우선 좌석 처리
        for seat in seats:
            if seat.get_attribute('sgn') == interpark_seat:
                if seat.find_elements_by_tag_name('span')[1].text != "매진":
                    seat.click()
                    if seat.find_elements_by_tag_name('span')[0].text == "그린존" or seat.find_elements_by_tag_name('span')[0].text == "일반석":
                        driver.execute_script('KBOGate.SetSeatAuto()')
                    else:
                        driver.execute_script("KBOGate.SetSeat()")
                        driver.switch_to_frame(driver.find_element_by_id('ifrmSeatDetail'))
                        available_seats = driver.find_elements_by_xpath("//td/img[@class='stySeat']")
                        for available_seat in available_seats:
                            available_seat.click()
                            driver.switch_to_window(driver.window_handles[1])
                            driver.switch_to_frame(driver.find_element_by_id('ifrmSeat'))
                            driver.find_element_by_xpath('//div[@class="btnWrap"]/a').click()
                            break
                    driver.switch_to_window(driver.window_handles[1])
                    driver.switch_to_frame(driver.find_element_by_id('ifrmBookStep'))
                    if interpark_he_is_sick:
                        if he_is_sick == "1":
                            driver.find_element_by_xpath("//select[@pricegradename='휠체어장애인+동반인']/option[text()='" + interpark_ticket_count + "']").click()
                        else:
                            driver.find_element_by_xpath("//select[@pricegradename='휠체어장애인']/option[text()='" + interpark_ticket_count + "']").click()
                    else:
                        driver.find_element_by_xpath("//select[@name='SeatCount']/option[text()='" + interpark_ticket_count + "']").click()
                    driver.switch_to_window(driver.window_handles[1])
                    driver.execute_script('fnNextStep()')
                    break
        # 우선 좌석이 매진일 경우
        for seat in seats:
            if seat.get_attribute('sgn') in interpark_seats :
                if seat.find_elements_by_tag_name('span')[1].text != "매진":
                    seat.click()
                    if seat.find_elements_by_tag_name('span')[0].text == "그린존" or seat.find_elements_by_tag_name('span')[0].text == "일반석":
                        driver.execute_script('KBOGate.SetSeatAuto()')
                    else:
                        driver.execute_script("KBOGate.SetSeat()")
                        driver.switch_to_frame(driver.find_element_by_id('ifrmSeatDetail'))
                        available_seats = driver.find_elements_by_xpath("//td/img[@class='stySeat']")
                        for available_seat in available_seats:
                            available_seat.click()
                            driver.switch_to_window(driver.window_handles[1])
                            driver.switch_to_frame(driver.find_element_by_id('ifrmSeat'))
                            driver.find_element_by_xpath('//div[@class="btnWrap"]/a').click()
                            break
                    driver.switch_to_window(driver.window_handles[1])
                    driver.switch_to_frame(driver.find_element_by_id('ifrmBookStep'))
                    driver.find_element_by_xpath("//select[@name='SeatCount']/option[text()='" + interpark_ticket_count + "']").click()
                    driver.switch_to_window(driver.window_handles[1])
                    driver.execute_script('fnNextStep()')
                    break
            else:
                continue