import os
import sys
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ========== Expiration ==========
CREATION_DATE = datetime(2025, 6, 26)
MAX_AGE_DAYS = 30
EXPIRATION_DATE = CREATION_DATE + timedelta(days=MAX_AGE_DAYS)
def check_expiration():
    if datetime.now() > EXPIRATION_DATE:
        sys.exit(f"This tool expired on {EXPIRATION_DATE.strftime('%b %d, %Y')}.")

check_expiration()

# ========== Selenium Browser Manager ==========
class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None

    def launch(self):
        if self.driver is not None:
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.get("https://west.ultrahhc.com/Home.aspx")
                self.driver.maximize_window()
                self.wait = WebDriverWait(self.driver, 12)
                return
            except Exception:
                pass
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://west.ultrahhc.com/Home.aspx")
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 12)

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.driver = None
        self.wait = None

browser_manager = BrowserManager()

# ========== Utilities ==========
def click_element(driver, element):
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)

# ========== SOC Section Autofills ==========
def autofill_administrative(driver, wait):
    try:
        for cid in ["A1005A","M0150_CPAY_1","12062","11644","12083","12088",
                    "12085","12086","12089","12087","12109","12119","A1250B","A1010A"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        for xpath in [
            "//input[@ng-model='oasis.oasisDetails.M0102_PHYSN_ORDRD_SOCROC_DT_NA']",
            "//input[@ng-model='oasis.oasisDetails.M1000_DC_NONE_14_DA']"
        ]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            el = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@ng-model='oasis.oasisDetails.M1005_INP_DSCHG_UNKNOWN']"
            )))
            driver.execute_script("arguments[0].removeAttribute('disabled')", el)
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='A1110B']")))
            Select(dd).select_by_value("0")
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@name='12075' and @value='No']")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "11641")))
            txt.clear(); txt.send_keys("002")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@ng-model='oasis.oasisDetails.A1110A']")))
            txt.clear(); txt.send_keys("English")
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "12081")))
            ta.clear()
            ta.send_keys(
                "Muscle weakness, unsteady gait, fall risk, impaired functional mobility and ADLs."
            )
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "12092")))
            txt.clear(); txt.send_keys("HTN, HLD, Unsteady Gait.")
        except: pass

    except Exception as e:
        print("Admin autofill error:", e)

def fill_hearing_speech_vision(driver, wait):
    try:
        for cid in ["12196","12262","12280","12287","12294"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        for field, val in [("select[mitemfield='B0200']","0"),
                           ("select[mitemfield='B1300']","0"),
                           ("select[mitemfield='B1000']","1")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, field)))
                Select(dd).select_by_value(val)
            except: pass
    except Exception as e:
        print("HSV autofill error:", e)

def fill_cognitive_patterns(driver, wait):
    try:
        for field in ["C0100","C1310A","C1310B","C1310C","C1310D"]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value("0")
            except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1700_COG_FUNCTION']")))
            Select(dd).select_by_value("00")
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//input[@ng-model='oasis.oasisDetails.POCMentalStatLoc19_0']")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        for field in ["M1710_WHEN_CONFUSED","M1720_WHEN_ANXIOUS"]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value("00")
            except: pass
    except Exception as e:
        print("Cognitive autofill error:", e)

def fill_mood(driver, wait):
    try:
        for field in ["D0150A1","D0150B1","D0700"]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value("0")
            except: pass
    except Exception as e:
        print("Mood autofill error:", e)

def fill_behavior(driver, wait):
    try:
        try:
            el = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[mitemfield='M1740_BD_6']")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1745_BEH_PROB_FREQ']")))
            Select(dd).select_by_value("00")
        except: pass

        for cid in ["10167","10191","10192","10207","10211"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10012")))
            txt.clear(); txt.send_keys("English")
        except: pass
    except Exception as e:
        print("Behavior autofill error:", e)

def fill_preferences(driver, wait):
    try:
        try:
            el = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//input[@ng-model='oasis.oasisDetails.M1100_PTNT_LVG_STUTN' and @ng-true-value=\"'06'\"]"
            )))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((By.ID, "8396")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        ids = ["8446","8447","8448","8449","8450","8451","8454","8455","8453","8440",
               "8475","8476","8478","8479","8477","8481","8480","8483","8486","8485",
               "8489","8484","8457","8460","8461","8464","8465","8471"]
        for cid in ids:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "8435")))
            ta.clear(); ta.send_keys("n/a")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M2100_CARE_TYPE_SRC_SPRVSN']")))
            Select(dd).select_by_value("01")
        except: pass
    except Exception as e:
        print("Preferences autofill error:", e)

def fill_functional_status(driver, wait):
    try:
        for sel in ["POCFuncLimLoc18_5","POCFuncLimLoc18_6","POCFuncLimLoc18_9"]:
            try:
                el = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"input[mitemfield='{sel}']")))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1800_CUR_GROOMING']")))
            Select(dd).select_by_value("02")
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "11653")))
            ta.clear(); ta.send_keys("AOx4, able to follow instructions")
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((By.ID, "11656")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "11661")))
            ta.clear(); ta.send_keys("n/a")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1810_CUR_DRESS_UPPER']")))
            Select(dd).select_by_value("02")
        except: pass

        for i in range(10361, 10387):
            try:
                txt = wait.until(EC.presence_of_element_located((By.ID, str(i))))
                txt.clear(); txt.send_keys("3+")
            except: pass

        for i in range(10387, 10400):
            try:
                txt = wait.until(EC.presence_of_element_located((By.ID, str(i))))
                txt.clear(); txt.send_keys("WFL")
            except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1820_CUR_DRESS_LOWER']")))
            Select(dd).select_by_value("02")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1830_CRNT_BATHG']")))
            Select(dd).select_by_value("03")
        except: pass

        for cid in ["10571","10573"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10589")))
            txt.clear(); txt.send_keys("NT")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10590")))
            txt.clear(); txt.send_keys("SBA")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1840_CUR_TOILTG']")))
            Select(dd).select_by_value("02")
        except: pass

        for cid in ["10413","10414","10415","10416","10417","10418","10419","10420"]:
            try:
                txt = wait.until(EC.presence_of_element_located((By.ID, cid)))
                txt.clear(); txt.send_keys("WFL")
            except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1845_CUR_TOILTG_HYGN']")))
            Select(dd).select_by_value("02")
        except: pass

        for cid in ["10629","10634","10637","10639","10641"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10737")))
            txt.clear(); txt.send_keys("NT")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10738")))
            txt.clear(); txt.send_keys("SBA")
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((By.ID, "10741")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        for field, val in [("M1850_CUR_TRNSFRNG","02"),("M1860_CRNT_AMBLTN","03")]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value(val)
            except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10775")))
            txt.clear(); txt.send_keys("Muscle weakness")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10776")))
            txt.clear()
            txt.send_keys(
                "Forward head lean, round shoulders, protracted scapula, slouch posture, increased Mid T-spine kyphosis."
            )
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10777")))
            txt.clear(); txt.send_keys("Fair-")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10789")))
            txt.clear(); txt.send_keys("SBA")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10791")))
            txt.clear()
            txt.send_keys(
                "Gait Analysis: Decreased step/stride length, slow cadence, wide BOS,"
                " forward trunk lean, decrease walking tolerance, decrease safety awareness and surrounding environment awareness."
            )
        except: pass

        for cid in ["10809","10819","10826","10830","10835","10840"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10842")))
            txt.clear(); txt.send_keys("17/28")
        except: pass

        for cid in ["10883","10887"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        for cid in ["10421","10422","10423","10424","10425"]:
            try:
                txt = wait.until(EC.presence_of_element_located((By.ID, cid)))
                txt.clear(); txt.send_keys("WFL")
            except: pass
    except Exception as e:
        print("Functional Status autofill error:", e)

def fill_functional_abilities_and_goals(driver, wait):
    try:
        for sel in ["POCActPermLoc18_3","POCActPermLoc18_4","POCActPermLoc18_10"]:
            try:
                el = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"input[mitemfield='{sel}']")))
                if not el.is_selected():
                    click_element(driver, el)
            except: pass

        for field, val in [("GG0100A","2"),("GG0100B","2"),("GG0100C","9"),("GG0100D","2")]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value(val)
            except: pass

        try:
            el = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[mitemfield='GG0110D']")))
            if not el.is_selected():
                click_element(driver, el)
        except: pass

        for field, val in [("GG0130A1","06"),("GG0130B1","06"),("GG0130C1","04"),
                           ("GG0130E1","03"),("GG0130F1","04"),("GG0130G1","03"),
                           ("GG0130H1","03")]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value(val)
            except: pass

        for field in ["GG0170A1","GG0170B1","GG0170C_MOBILITY_SOCROC_PERF",
                      "GG0170D1","GG0170E1","GG0170F1"]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value("04")
            except: pass

        for field in ["GG0170I1","GG0170J1","GG0170G1","GG0170K1",
                      "GG0170L1","GG0170M1","GG0170N1","GG0170O1"]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value("88")
            except: pass

        for field, val in [("GG0170P1","04"),("GG0170Q1","0")]:
            try:
                dd = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"select[mitemfield='{field}']")))
                Select(dd).select_by_value(val)
            except: pass
    except Exception as e:
        print("FABG autofill error:", e)

def fill_bladder_and_bowel(driver, wait):
    try:
        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1600_UTI']")))
            Select(dd).select_by_value("00")
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((By.ID, "9609")))
            if not el.is_selected(): click_element(driver, el)
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1610_UR_INCONT']")))
            Select(dd).select_by_value("00")
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "6278")))
            ta.clear(); ta.send_keys("N/A")
        except: pass

        for cid in ["9700","9765"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected(): click_element(driver, el)
            except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "9768")))
            txt.clear(); txt.send_keys("1")
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "9777")))
            ta.clear(); ta.send_keys("N/A")
        except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((By.ID, "9778")))
            if not el.is_selected(): click_element(driver, el)
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1620_BWL_INCONT']")))
            Select(dd).select_by_value("00")
        except: pass

        for cid in ["9867","9900","9952"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected(): click_element(driver, el)
            except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1630_OSTOMY']")))
            Select(dd).select_by_value("00")
        except: pass
    except Exception as e:
        print("Bladder&Bowel autofill error:", e)

def fill_active_diagnoses(driver, wait):
    try:
        for cid in ["13695","13704","13704","13701","13697","13698","13693"]:
            try:
                chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not chk.is_selected(): click_element(driver, chk)
            except: pass

        try:
            el = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "input[mitemfield='M1028_DM_PAD_2']"
            )))
            if not el.is_selected(): click_element(driver, el)
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "13711")))
            txt.clear(); txt.send_keys("30")
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "13718")))
            ta.clear()
            ta.send_keys(
                "Patient education on safety and precautions during functional mobility, "
                "fall prevention strategies, proper use of assistive devices, correct body mechanics "
                "for gait and transfers, and balance training."
            )
        except: pass

        try:
            olds = driver.find_elements(By.XPATH,
                "//input[@ng-model='oasis.oasisDetails.POCPrognosisLoc20' and @ng-true-value='0']")
            for el in olds:
                driver.execute_script("arguments[0].remove()", el)
        except: pass

        try:
            new_chk = wait.until(EC.element_to_be_clickable((By.XPATH,
                "//input[@ng-model='oasis.oasisDetails.POCPrognosisLoc20' and @ng-true-value='3']")))
            if not new_chk.is_selected(): click_element(driver, new_chk)
        except: pass
    except Exception as e:
        print("Active Diagnoses autofill error:", e)

def fill_health_conditions(driver, wait):
    try:
        try:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                "input[mitemfield='M1032_HOSP_6']")))
            if not chk.is_selected(): click_element(driver, chk)
        except: pass

        try:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                "input[mitemfield='M1032_HOSP_8']")))
            if not chk.is_selected(): click_element(driver, chk)
        except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "8361")))
            ta.clear(); ta.send_keys("Fall Risk.")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='J0510']")))
            Select(dd).select_by_value("3")
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "12801")))
            txt.clear(); txt.send_keys("4/10")
        except: pass

        for cid in ["12807","12818","12814"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected(): click_element(driver, el)
            except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "12828")))
            ta.clear(); ta.send_keys(
                "Limits functional mobility, difficulty with ADLs, difficulty prolong walking/standing, and unsafe with transfers."
            )
        except: pass

        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "12845")))
            txt.clear(); txt.send_keys("Chronic")
        except: pass

        for cid, val in [("12846","4/10"),("12847","7/10"),("12848","0/10")]:
            try:
                txt = wait.until(EC.presence_of_element_located((By.ID, cid)))
                txt.clear(); txt.send_keys(val)
            except: pass

        for cid in ["12990","12990","12984","12978","12980","12981","12971","12964","12962","12960"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected(): click_element(driver, el)
            except: pass

        try:
            ta = wait.until(EC.presence_of_element_located((By.ID, "12959")))
            ta.clear(); ta.send_keys("MD prescribed HH PT.")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='J0520']")))
            Select(dd).select_by_value("3")
        except: pass

        for cid in ["9453","9459","9465","9471","9475","9463","9458","9434","9438","9485"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected(): click_element(driver, el)
            except: pass

        for cid in ["9490","9491","9492","9493","9494","9495"]:
            try:
                txt = wait.until(EC.presence_of_element_located((By.ID, cid)))
                txt.clear(); txt.send_keys("Clear")
            except: pass

        for cid in ["9579","9580"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not el.is_selected(): click_element(driver, el)
            except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='M1400_WHEN_DYSPNEIC']")))
            Select(dd).select_by_value("01")
        except: pass

        try:
            dd = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "select[mitemfield='J0530']")))
            Select(dd).select_by_value("3")
        except: pass
    except Exception as e:
        print("Health Conditions autofill error:", e)

def fill_swallowing_nutritional_status(driver, wait):
    try:
        adv_chk = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "input[mitemfield='AdvanceDirectives_6']"
        )))
        if not adv_chk.is_selected(): click_element(driver, adv_chk)
        adv_txt = wait.until(EC.presence_of_element_located((By.ID, "adv_others")))
        adv_txt.clear()
        adv_txt.send_keys("Information Provided")
    except: pass

    try:
        k_chk = wait.until(EC.element_to_be_clickable((By.ID, "K0520Z1")))
        if not k_chk.is_selected(): click_element(driver, k_chk)
    except: pass

    try:
        dd = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M1870_CUR_FEEDING']")))
        Select(dd).select_by_value("01")
    except: pass

def fill_skin_conditions(driver, wait):
    try:
        for cid in ["9133","9208","9211","9277"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)

        Select(wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M1306_UNHLD_STG2_PRSR_ULCR']"))))\
            .select_by_value("0")

        Select(wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M1322_NBR_PRSULC_STG1']"))))\
            .select_by_value("00")

        Select(wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M1324_STG_PRBLM_ULCER']"))))\
            .select_by_value("NA")

        Select(wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M1330_STAS_ULCR_PRSNT']"))))\
            .select_by_value("00")

        Select(wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M1340_SRGCL_WND_PRSNT']"))))\
            .select_by_value("00")

        txt = wait.until(EC.presence_of_element_located((By.ID, "9127"))); txt.clear(); txt.send_keys("N/A")
        txt = wait.until(EC.presence_of_element_located((By.ID, "9309"))); txt.clear(); txt.send_keys("NA")
    except Exception as e:
        print("Skin Conditions autofill error:", e)

def fill_medications(driver, wait):
    try:
        chk = wait.until(EC.element_to_be_clickable((By.ID, "N0415Z1")))
        if not chk.is_selected(): click_element(driver, chk)

        dd = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M2000_DRUG_RGMN_RVW']")))
        Select(dd).select_by_value("0")

        dd = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M2010_HIGH_RISK_DRUG_EDCTN']")))
        Select(dd).select_by_value("NA")

        dd = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M2020_CRNT_MGMT_ORAL_MDCTN']")))
        Select(dd).select_by_value("02")

        dd = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "select[mitemfield='M2030_CRNT_MGMT_INJCTN_MDCTN']")))
        Select(dd).select_by_value("NA")

        chk = wait.until(EC.element_to_be_clickable((By.ID, "13836")))
        if not chk.is_selected(): click_element(driver, chk)
        chk = wait.until(EC.element_to_be_clickable((By.ID, "13839")))
        if not chk.is_selected(): click_element(driver, chk)

        ta = wait.until(EC.presence_of_element_located((By.ID, "13844")))
        ta.clear(); ta.send_keys("NA")

        chk = wait.until(EC.element_to_be_clickable((By.ID, "13845")))
        if not chk.is_selected(): click_element(driver, chk)
    except Exception as e:
        print("Medications autofill error:", e)

def fill_special_treatment(driver, wait):
    try:
        for cid in ["11736","11741","11742","11743","11747","11748","11749"]:
            chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not chk.is_selected(): click_element(driver, chk)

        ta = wait.until(EC.presence_of_element_located((By.ID, "11745"))); ta.clear(); ta.send_keys("N/A")
        ta = wait.until(EC.presence_of_element_located((By.ID, "11751"))); ta.clear(); ta.send_keys("N/A")
        ta = wait.until(EC.presence_of_element_located((By.ID, "11754")))
        ta.clear()
        ta.send_keys(
            "Good motivation, positive attitude toward recovery, strong social support "
            "(family or caregiver), proactive in recovery, good insight into their limitations, "
            "applies safety strategies."
        )
        ta = wait.until(EC.presence_of_element_located((By.ID, "11756")))
        ta.clear()
        ta.send_keys(
            "Pain and rapid fatigue during activities, reducing motivation and consistency "
            "with HEP and ADLs. B LE strength deficits, and requires assistance for all functional mobility."
        )
        ta = wait.until(EC.presence_of_element_located((By.ID, "11758")))
        ta.clear()
        ta.send_keys(
            "Limited lower-extremity strength and endurance heighten fall risk and restrict full "
            "participation in therapy, potentially delaying progress toward their functional goals."
        )
        ta = wait.until(EC.presence_of_element_located((By.ID, "11580"))); ta.clear(); ta.send_keys("N/A")

        for cid in ["11611","11603","11608","11612"]:
            chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not chk.is_selected(): click_element(driver, chk)

        ta = wait.until(EC.presence_of_element_located((By.ID, "11588"))); ta.clear(); ta.send_keys("None")
        ta = wait.until(EC.presence_of_element_located((By.ID, "5924")))
        ta.clear()
        ta.send_keys(
            "PT evaluation and home safety assessment—including DME evaluation—were completed. "
            "The patient received instruction on their daily HEP, safe movement mechanics, "
            "proper use of DME/AD, and fall-prevention strategies. A detailed PT plan of care "
            "was developed, with specific short- and long-term goals established to guide "
            "interventions and measure progress toward functional outcomes."
        )

        for cid in [
            "6015","6017","6018","6032","6034","6039","6048","6052",
            "11761","11766","11768","11767","11770","11772","11771",
            "11773","11776","11777","11778"
        ]:
            chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not chk.is_selected(): click_element(driver, chk)

        txt = wait.until(EC.presence_of_element_located((By.ID, "6040"))); txt.clear(); txt.send_keys("Agency Case Manager")
        txt = wait.until(EC.presence_of_element_located((By.ID, "6050"))); txt.clear(); txt.send_keys("NA")
        ta = wait.until(EC.presence_of_element_located((By.ID, "11784"))); ta.clear(); ta.send_keys("N/A")

        for cid in ["11786","11787","11788","11790","11793"]:
            chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not chk.is_selected(): click_element(driver, chk)
        ta = wait.until(EC.presence_of_element_located((By.ID, "11797"))); ta.clear(); ta.send_keys("N/A")

        chk = wait.until(EC.element_to_be_clickable((By.ID, "O0110Z1A")))
        if not chk.is_selected(): click_element(driver, chk)
        for cid in ["6514","6516","6517","6518","6519","6520","6522","6523"]:
            chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not chk.is_selected(): click_element(driver, chk)

        for selector in [
            "input[mitemfield='POCSafetyMeasuresLoc15_3']",
            "input[mitemfield='POCSafetyMeasuresLoc15_11']"
        ]:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            if not chk.is_selected(): click_element(driver, chk)

        for cid in ["6710","6715","6704","6636","6639","6640","6642","6648","6667"]:
            chk = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not chk.is_selected(): click_element(driver, chk)
    except Exception as e:
        print("Special Treatment autofill error:", e)


# ===== RECERT SECTION AUTOFILLS =====

def recert_autofill_administrative(driver, wait):
    try:
        click_element(driver, wait.until(EC.element_to_be_clickable((By.ID, "M0150_CPAY_1"))))
        click_element(driver, wait.until(EC.element_to_be_clickable((By.ID, "12062"))))
        click_element(driver, wait.until(EC.element_to_be_clickable((
            By.XPATH, "//input[@type='radio' and @name='12075' and @value='No']"
        ))))
        Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
            "select[mitemfield='M0080_ASSESSOR_DISCIPLINE']")))).select_by_value("02")
        fld = wait.until(EC.presence_of_element_located((By.ID, "11641"))); fld.clear(); fld.send_keys("002")
        js = """
            let sel = document.querySelector("select[mitemfield='M0100_ASSMT_REASON']");
            sel.value = '04';
            sel.dispatchEvent(new Event('change'));
        """
        driver.execute_script(js)
    except Exception as e:
        print("RECERT Admin autofill error:", e)

def recert_fill_functional_status(driver, wait):
    try:
        el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[mitemfield='POCMentalStatLoc19_2']")))
        if not el.is_selected(): click_element(driver, el)
        for field in ["POCFuncLimLoc18_5","POCFuncLimLoc18_6","POCFuncLimLoc18_9"]:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[mitemfield='{field}']")))
            if not chk.is_selected(): click_element(driver, chk)
        groom = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1800_CUR_GROOMING']")))
        Select(groom).select_by_value("02")
        for cid in ["5511","5515","5555","5569","5560","5584","5561","5553","5585"]:
            box = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not box.is_selected(): click_element(driver, box)
        tf = wait.until(EC.presence_of_element_located((By.ID, "5578"))); tf.clear(); tf.send_keys("35")
        ta = wait.until(EC.presence_of_element_located((By.ID, "5577"))); ta.clear(); ta.send_keys(
            "Patient education on safety and precautions during functional mobility, "
            "fall prevention strategies, proper use of assistive devices, correct body "
            "mechanics for gait and transfers, and balance training."
        )
        for tid in ["10527","10529"]:
            txt = wait.until(EC.presence_of_element_located((By.ID, tid))); txt.clear(); txt.send_keys("n/a")
        ta2 = wait.until(EC.presence_of_element_located((By.ID, "11653"))); ta2.clear(); ta2.send_keys("Able to follow PT instructions when prompted to perform tasks.")
        for cid in ["11656","11659"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta3 = wait.until(EC.presence_of_element_located((By.ID, "11661"))); ta3.clear(); ta3.send_keys("n/a")
        dress = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1810_CUR_DRESS_UPPER']"))); Select(dress).select_by_value("02")
        for tid, val in [
            ("10479","3"), ("10480","3"), ("10481","3"), ("10482","3"),
            ("10484","3"), ("10486","n/a"), ("10487","4"), ("10488","4"),
            ("10490","3"), ("10489","2")
        ]:
            txt = wait.until(EC.presence_of_element_located((By.ID, tid))); txt.clear(); txt.send_keys(val)
        lower = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1820_CUR_DRESS_LOWER']"))); Select(lower).select_by_value("02")
        bath = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1830_CRNT_BATHG']"))); Select(bath).select_by_value("03")
        for cid in ["10571","10573"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        for tid, val in [("10589","Min A"), ("10590","SBA")]:
            txt = wait.until(EC.presence_of_element_located((By.ID, tid))); txt.clear(); txt.send_keys(val)
        toil = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1840_CUR_TOILTG']"))); Select(toil).select_by_value("01")
        for cid in ["10629","10634","10637","10639","10641"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        cb = wait.until(EC.element_to_be_clickable((By.ID, "10741")))
        if not cb.is_selected(): click_element(driver, cb)
        for tid, val in [("10738","SBA"), ("10737","Min A")]:
            txt = wait.until(EC.presence_of_element_located((By.ID, tid))); txt.clear(); txt.send_keys(val)
        trns = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1850_CUR_TRNSFRNG']"))); Select(trns).select_by_value("02")
        amb = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1860_CRNT_AMBLTN']"))); Select(amb).select_by_value("03")
        txt = wait.until(EC.presence_of_element_located((By.ID, "10775"))); txt.clear(); txt.send_keys("Muscle Weakness")
        txt = wait.until(EC.presence_of_element_located((By.ID, "10776"))); txt.clear(); txt.send_keys("forward head posture, rounded shoulder, t/s kyphosis")
        txt = wait.until(EC.presence_of_element_located((By.ID, "10777"))); txt.clear(); txt.send_keys("Poor+")
        txt = wait.until(EC.presence_of_element_located((By.ID, "10791"))); txt.clear(); txt.send_keys("Small step length, unsteady")
        cb = wait.until(EC.element_to_be_clickable((By.ID, "10809")))
        if not cb.is_selected(): click_element(driver, cb)
        txt = wait.until(EC.presence_of_element_located((By.ID, "10821"))); txt.clear(); txt.send_keys("FWW")
        for cid in ["10819","10826"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        for cid in ["10831","10835","10840"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        txt = wait.until(EC.presence_of_element_located((By.ID, "10842"))); txt.clear(); txt.send_keys("18/28")
        for cid in ["10875","10878"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        cb = wait.until(EC.element_to_be_clickable((By.ID, "10857")))
        if not cb.is_selected(): click_element(driver, cb)
    except Exception as e:
        print("RECERT Functional Status autofill error:", e)

def recert_fill_functional_abilities_and_goals(driver, wait):
    try:
        for field in ["POCActPermLoc18_2", "POCActPermLoc18_3", "POCActPermLoc18_4", "POCActPermLoc18_10"]:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[mitemfield='{field}']")))
            if not chk.is_selected(): click_element(driver, chk)
        for field in ["POCSafetyMeasuresLoc15_3","POCSafetyMeasuresLoc15_11","POCSafetyMeasuresLoc15_7"]:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[mitemfield='{field}']")))
            if not chk.is_selected(): click_element(driver, chk)
        for fld in ["GG0130A4","GG0130B4","GG0130C4"]:
            dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value("05")
        for fld in ["GG0170A4","GG0170B4","GG0170C4","GG0170D4","GG0170E4","GG0170F4"]:
            dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value("04")
        for fld in ["GG0170I4","GG0170J4"]:
            dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value("04")
        for fld in ["GG0170L4","GG0170M4"]:
            dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value("88")
        q4 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='GG0170Q4']"))); Select(q4).select_by_value("0")
    except Exception as e:
        print("RECERT FABG autofill error:", e)

def recert_fill_health_conditions(driver, wait):
    try:
        for fld in ["M1032_HOSP_6", "M1032_HOSP_7"]:
            chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[mitemfield='{fld}']")))
            if not chk.is_selected(): click_element(driver, chk)
        for cid in ["12738", "12741", "12750", "12748"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        txt = wait.until(EC.presence_of_element_located((By.ID, "12735"))); txt.clear(); txt.send_keys("4/10")
        ta = wait.until(EC.presence_of_element_located((By.ID, "12762"))); ta.clear(); ta.send_keys("Limit functional mobility, activity tolerance, and limit gait.")
        for cid in ["12904","12897","12894","12893","12892","12895","12888"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        for cid in ["12885","12878","12876","12874","12875"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        ta = wait.until(EC.presence_of_element_located((By.ID, "12896"))); ta.clear(); ta.send_keys("Functional movement:")
        ta = wait.until(EC.presence_of_element_located((By.ID, "12873"))); ta.clear(); ta.send_keys("MD refer to HH PT.")
        for cid in ["13254","13259","13260","13266","13272","13264","13276"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        for cid in ["12148","12172","12213","12220"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        txt = wait.until(EC.presence_of_element_located((By.ID, "12778"))); txt.clear(); txt.send_keys("Chronic")
        for tid, val in [("12777","3/10"),("12779","6/10"),("12780","1/10")]:
            txt = wait.until(EC.presence_of_element_located((By.ID, tid))); txt.clear(); txt.send_keys(val)
        ta = wait.until(EC.presence_of_element_located((By.ID, "12781"))); ta.clear(); ta.send_keys("Dull/ache/tension/sharp")
        el = wait.until(EC.element_to_be_clickable((By.ID, "13286")))
        if not el.is_selected(): click_element(driver, el)
        for tid in ["13291","13292","13293","13294","13295","13296"]:
            txt = wait.until(EC.presence_of_element_located((By.ID, tid))); txt.clear(); txt.send_keys("clear")
        for cid in ["13381","13380"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13409"))); ta.clear(); ta.send_keys("n/a")
        el = wait.until(EC.element_to_be_clickable((By.ID, "13453")))
        if not el.is_selected(): click_element(driver, el)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13477"))); ta.clear(); ta.send_keys("n/a")
        for cid in ["13478","13513","13601","13621","13851","13854","13860"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13539"))); ta.clear(); ta.send_keys("n/a")
        dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1700_COG_FUNCTION']"))); Select(dd).select_by_value("01")
        fair_cb = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[ng-model='oasis.oasisDetails.POCPrognosisLoc20']")))
        if not fair_cb.is_selected(): click_element(driver, fair_cb)
        chk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[mitemfield='AdvanceDirectives_6']")))
        if not chk.is_selected(): click_element(driver, chk)
        ta = wait.until(EC.presence_of_element_located((By.ID, "adv_others"))); ta.clear(); ta.send_keys("Information provided")
    except Exception as e:
        print("RECERT Health Conditions autofill error:", e)

def recert_fill_skin_conditions(driver, wait):
    try:
        cb = wait.until(EC.element_to_be_clickable((By.ID, "4401")))
        if not cb.is_selected(): click_element(driver, cb)
        cb = wait.until(EC.element_to_be_clickable((By.ID, "4404")))
        if not cb.is_selected(): click_element(driver, cb)
        dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1306_UNHLD_STG2_PRSR_ULCR']"))); Select(dd).select_by_value("0")
        cb = wait.until(EC.element_to_be_clickable((By.ID, "13078")))
        if not cb.is_selected(): click_element(driver, cb)
        txt = wait.until(EC.presence_of_element_located((By.ID, "13110"))); txt.clear(); txt.send_keys("n/a")
        ta = wait.until(EC.presence_of_element_located((By.ID, "4416"))); ta.clear(); ta.send_keys("n/a")
    except Exception as e:
        print("RECERT Skin Conditions autofill error:", e)

def recert_fill_active_diagnoses(driver, wait):
    try:
        ta = wait.until(EC.presence_of_element_located((By.ID, "13867"))); ta.clear(); ta.send_keys("Able to follow PT instructions, show participation, and follow PT POC.")
        ta = wait.until(EC.presence_of_element_located((By.ID, "13870"))); ta.clear(); ta.send_keys("Poor balance, strength deficits, gait impairment, poor activity tolerance, decrease safety awareness.")
        ta = wait.until(EC.presence_of_element_located((By.ID, "13874"))); ta.clear(); ta.send_keys("Lead to high fall risk, risk for injury, slow down progress with POC.")
        ta = wait.until(EC.presence_of_element_located((By.ID, "13876"))); ta.clear(); ta.send_keys("Provide HH PT with verbal education, tactile guidance, demonstration, illustration, and ongoing pt/family education.")
        ta = wait.until(EC.presence_of_element_located((By.ID, "13880"))); ta.clear(); ta.send_keys("n/a")
        for cid in ["13881", "13886", "13887", "13888"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13890"))); ta.clear(); ta.send_keys("n/a")
        for cid in ["13892", "13893", "13894"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13896"))); ta.clear(); ta.send_keys("n/a")
        for cid in ["13898", "13899", "13900", "13902", "13905"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        cb = wait.until(EC.element_to_be_clickable((By.ID, "13904")))
        if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13909"))); ta.clear(); ta.send_keys("Decrease safety awareness, impaired balance, poor activity tolerance, gross strength deficits, reliant on use of AD.")
        for cid in ["13971","13972","13973","13974","13975","13978","13977","13979","13965"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "13953"))); ta.clear(); ta.send_keys("HEP, Fall Prevention education, proper use of AD")
        for cid in ["13980","13981","13985"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        for cid in ["14003","13997","14005","14008"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        for cid in ["14009","14007","14006"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "14011"))); ta.clear(); ta.send_keys(
            "PT re-evaluation and home safety assessment—including DME re-evaluation—were completed. "
            "The patient received instruction on daily HEP, safe movement mechanics, proper use of DME/AD, "
            "and fall-prevention strategies. A detailed PT plan of care was developed, with specific "
            "short- and long-term goals established to guide interventions and measure progress toward "
            "functional outcomes."
        )
        ta = wait.until(EC.presence_of_element_located((By.ID, "14013"))); ta.clear(); ta.send_keys("Pt/CG acknowledge PT POC.")
        for cid in ["14222","14223","14225","14224","14228","14228","14234","14239","14244","14246","14254"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "14252"))); ta.clear(); ta.send_keys("HEP, fall prevention, functional mobility/gait training.")
        for cid in ["14258","14261","14262","14272","14274","14279"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        txt = wait.until(EC.presence_of_element_located((By.ID, "14280"))); txt.clear(); txt.send_keys("Agency CM")
        for cid in ["14515","14517","14519","14520","14523","14521"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        for cid in ["14615","14618","14619","14621","14626","14646","14681","14685","14689"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        for cid in ["14694","14707"]:
            cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "14701"))); ta.clear(); ta.send_keys(
            "Patient has been receiving skilled home health PT to address functional mobility deficits "
            "secondary to muscle weakness, impaired balance, and unsteady gait. Currently, patient is "
            "progressing slowly and still has difficulty with functional bed mobility, transfer, decreased "
            "gait tolerance, unsteady gait, and poor balance leading to high fall risk. Patient/CG will need "
            "further training with HEP, fall prevention, and safety with functional mobility to decrease "
            "fall risk and meet goals. Patient still has potential and will continue to benefit from further "
            "skilled HH PT to work toward personal goals, as well as, improve overall ADLs."
        )
        cb = wait.until(EC.element_to_be_clickable((By.ID, "14717")))
        if not cb.is_selected(): click_element(driver, cb)
        ta = wait.until(EC.presence_of_element_located((By.ID, "14728"))); ta.clear(); ta.send_keys("High fall risk, impaired functional mobility and gait.")
        ta = wait.until(EC.presence_of_element_located((By.ID, "14734"))); ta.clear(); ta.send_keys("Pt educated on DC plans")
        ta = wait.until(EC.presence_of_element_located((By.ID, "14736"))); ta.clear(); ta.send_keys(
            "Some progression seen, still need further PT to improve functional mobility/gait while decrease fall risk."
        )
    except Exception as e:
        print("RECERT Active Diagnoses autofill error:", e)

# ===== DCO SECTION AUTOFILLS =====

def dco_autofill_administrative(driver, wait):
    try:
        for cid in ["12062", "8177", "8182"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @name='12075' and @value='No']")))
        if not radio.is_selected(): click_element(driver, radio)
        ag = wait.until(EC.presence_of_element_located((By.ID, "8183"))); ag.clear(); ag.send_keys("Agency CM")
        el = wait.until(EC.element_to_be_clickable((By.ID, "8185")));
        if not el.is_selected(): click_element(driver, el)
        ta = wait.until(EC.presence_of_element_located((By.ID, "8193"))); ta.clear(); ta.send_keys("Muscle weakness, gait/balance impairment, fall risk")
        ta = wait.until(EC.presence_of_element_located((By.ID, "8196")));
        ta.clear(); ta.send_keys("PT POC Completed. Patient currently requires SBA for bed mobility, transfers, and ambulation for 100 feet with the use of an assistive device. Partial progress has been made toward established goals with PT treatment. It is recommended that the patient continue with daily HEP to support ongoing improvements and maintain current functional mobility and activity tolerance. Patient/CG is advised to follow up with the primary care provider as needed or if any new symptoms arise.")
        for cid in ["8198", "8206", "8223"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        goals = wait.until(EC.presence_of_element_located((By.ID, "8224"))); goals.clear(); goals.send_keys("goals partially met, no further PT tx needed at this time and recommend to try Indep HEP for continuation improvement/maintain current functional condition. Follow up with PCP prn.")
        ta2 = wait.until(EC.presence_of_element_located((By.ID, "8227")));
        ta2.clear(); ta2.send_keys("Pt review on fall/safety precautions with ADLs and functional mobility. Pt review HEP with emphasis on safety and proper body mechanics. Continue with daily HEP as instructed. Continue to use AD as prescribed and/or prn.")
        for cid in ["8229","8230","8231","8232","8233","8235","8239","8243","A1250B"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"select[mitemfield='M2300_EMER_USE_AFTR_LAST_ASMT']"))); Select(dd).select_by_value("00")
        ta3 = wait.until(EC.presence_of_element_located((By.ID, "11918"))); ta3.clear(); ta3.send_keys("Good motivation, positive attitude toward recovery, strong social support")
        for cid in ["11920","11921","11922"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        ta4 = wait.until(EC.presence_of_element_located((By.ID, "11930"))); ta4.clear(); ta4.send_keys("Limited lower-extremity strength, reduce endurance, decrease safety awareness, decrease judgement and decision making.")
        ta5 = wait.until(EC.presence_of_element_located((By.ID, "11932"))); ta5.clear(); ta5.send_keys("HTN, arthritis, muscle atrophy, balance/gait abnormality.")
        ta6 = wait.until(EC.presence_of_element_located((By.ID, "11934"))); ta6.clear(); ta6.send_keys("provide instruction through verbal, tactile, demonstration, illustration. Fall/injury prevention education.")
        for cid in ["11935","11938","11940","11943","11946","11948","11959","11961"]:
            el = wait.until(EC.element_to_be_clickable((By.ID, cid)))
            if not el.is_selected(): click_element(driver, el)
        ta7 = wait.until(EC.presence_of_element_located((By.ID, "11957"))); ta7.clear(); ta7.send_keys("n/a")
        dd2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M2410_INPAT_FACILITY']"))); Select(dd2).select_by_value("NA")
        dd3 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M2420_DSCHRG_DISP']"))); Select(dd3).select_by_value("01")
        ta8 = wait.until(EC.presence_of_element_located((By.ID, "6766"))); ta8.clear(); ta8.send_keys("PT discharge, home environment assessment, and DME assessment have been completed. Patient was instructed and educated on the importance of adhering to a daily HEP to maintain strength, mobility, and function. Fall prevention strategies and home safety measures were reviewed and reinforced. Recommend continue with Indep HEP and DC to family/CG care/support.")
        dd5 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='A2123']"))); Select(dd5).select_by_value("1")
        el = wait.until(EC.element_to_be_clickable((By.ID, "A2124C")));
        if not el.is_selected(): click_element(driver, el)
    except Exception as e:
        print("DCO Admin autofill error:", e)

def dco_fill_hearing_speech_vision(driver, wait):
    try:
        dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='B1300']"))); Select(dd).select_by_value("4")
    except Exception as e:
        print("DCO HSV autofill error:", e)

def dco_fill_cognitive_patterns(driver, wait):
    try:
        for _ in range(2):
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='C0100']"))); Select(dd).select_by_value("0")
            except: pass
        for fld in ["C1310A","C1310B","C1310C","C1310D","M1700_COG_FUNCTION","M1710_WHEN_CONFUSED","M1720_WHEN_ANXIOUS"]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']")))
                if fld.startswith("C1310"):
                    Select(dd).select_by_value("0")
                elif fld == "M1700_COG_FUNCTION":
                    Select(dd).select_by_value("01")
                elif fld == "M1710_WHEN_CONFUSED":
                    Select(dd).select_by_value("01")
                else:
                    Select(dd).select_by_value("00")
            except: pass
        try:
            chk = wait.until(EC.element_to_be_clickable((By.ID, "9960")));
            if not chk.is_selected(): click_element(driver, chk)
        except: pass
    except Exception as e:
        print("DCO Cognitive autofill error:", e)

def dco_fill_mood(driver, wait):
    try:
        for fld in ["D0150A1","D0150B1","D0700"]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']")))
                Select(dd).select_by_value("0")
            except: pass
    except Exception as e:
        print("DCO Mood autofill error:", e)

def dco_fill_behavior(driver, wait):
    try:
        for fld in ["M1740_BD_6"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[mitemfield='{fld}']")));
                if not el.is_selected(): click_element(driver, el)
            except: pass
        try:
            dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1745_BEH_PROB_FREQ']"))); Select(dd).select_by_value("00")
        except: pass
        for cid in ["10167","10191","10192","10207","10211"]:
            try:
                el = wait.until(EC.element_to_be_clickable((By.ID, cid)));
                if not el.is_selected(): click_element(driver, el)
            except: pass
        try:
            txt = wait.until(EC.presence_of_element_located((By.ID, "10012"))); txt.clear(); txt.send_keys("English")
        except: pass
    except Exception as e:
        print("DCO Behavior autofill error:", e)

def dco_fill_preferences(driver, wait):
    try:
        for fld,val in [("M2100_CARE_TYPE_SRC_ADL","01"),("M2100_CARE_TYPE_SRC_MDCTN","01"),("M2100_CARE_TYPE_SRC_PRCDR","01"),("M2100_CARE_TYPE_SRC_SPRVSN","01")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
    except Exception as e:
        print("DCO Preferences autofill error:", e)

def dco_fill_functional_status(driver, wait):
    try:
        for fld,val in [("M1800_CUR_GROOMING","02"),("M1810_CUR_DRESS_UPPER","02")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
        for tid in ["10479","10480","10481","10482","10484"]:
            try:
                tbox = wait.until(EC.presence_of_element_located((By.ID, tid))); tbox.clear(); tbox.send_keys("3")
            except: pass
        try:
            tbox8 = wait.until(EC.presence_of_element_located((By.ID, "10487"))); tbox8.clear(); tbox8.send_keys("4")
        except: pass
        for tid in ["10488","10490"]:
            try:
                tbox = wait.until(EC.presence_of_element_located((By.ID, tid))); tbox.clear(); tbox.send_keys("3")
            except: pass
        try:
            tbox11 = wait.until(EC.presence_of_element_located((By.ID, "10489"))); tbox11.clear(); tbox11.send_keys("2")
        except: pass
        for fld,val in [("M1820_CUR_DRESS_LOWER","02"),("M1830_CRNT_BATHG","03")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
        for cid in ["10571","10573"]:
            try:
                cb = wait.until(EC.element_to_be_clickable((By.ID, cid)));
                if not cb.is_selected(): cb.click()
            except: pass
        try:
            box15 = wait.until(EC.presence_of_element_located((By.ID, "10590"))); box15.clear(); box15.send_keys("SBA")
        except: pass
        for fld,val in [("M1840_CUR_TOILTG","01"),("M1845_CUR_TOILTG_HYGN","02")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
        for cid in ["10629","10634","10637","10639","10641","10741"]:
            try:
                cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not cb.is_selected(): cb.click()
            except: pass
        try:
            box19 = wait.until(EC.presence_of_element_located((By.ID, "10738"))); box19.clear(); box19.send_keys("SBA")
        except: pass
        for fld,val in [("M1850_CUR_TRNSFRNG","02"),("M1860_CRNT_AMBLTN","03")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
        try:
            box22 = wait.until(EC.presence_of_element_located((By.ID, "10775"))); box22.clear(); box22.send_keys("Muscle Weakness")
        except: pass
        try:
            box23 = wait.until(EC.presence_of_element_located((By.ID, "10776"))); box23.clear(); box23.send_keys("Forward head lean, round shoulders, protracted scapula, slouch posture")
        except: pass
        try:
            box24 = wait.until(EC.presence_of_element_located((By.ID, "10777"))); box24.clear(); box24.send_keys("Fair")
        except: pass
        try:
            box25 = wait.until(EC.presence_of_element_located((By.ID, "10789"))); box25.clear(); box25.send_keys("SBA")
        except: pass
        try:
            box26 = wait.until(EC.presence_of_element_located((By.ID, "10790"))); box26.clear(); box26.send_keys("FWW")
        except: pass
        try:
            box27 = wait.until(EC.presence_of_element_located((By.ID, "10791")));
            box27.clear(); box27.send_keys("Gait Analysis: Decreased step/stride length, slow cadence, wide BOS, forward trunk lean, decrease walking tolerance, decrease safety awareness and surrounding environment awareness.")
        except: pass
        for cid in ["10809","10819","10826","10831","10835","10840","10857"]:
            try:
                cb = wait.until(EC.element_to_be_clickable((By.ID, cid)))
                if not cb.is_selected(): cb.click()
            except: pass
        try:
            box29 = wait.until(EC.presence_of_element_located((By.ID, "10842"))); box29.clear(); box29.send_keys("19/28")
        except: pass
    except Exception as e:
        print("DCO Functional Status autofill error:", e)

def dco_fill_functional_abilities_and_goals(driver, wait):
    try:
        for fld,val in [("GG0130A3","05"),("GG0130B3","05"),("GG0130C3","04"),
                        ("GG0130E3","03"),("GG0130F3","04"),("GG0130G3","03"),
                        ("GG0130H3","03")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
        for fld,val in [("GG0170A3","04"),("GG0170B3","04"),("GG0170C3","04"),
                        ("GG0170D3","04"),("GG0170E3","04"),("GG0170F3","04"),
                        ("GG0170G3","88"),("GG0170I3","04"),("GG0170J3","04"),
                        ("GG0170K3","88"),("GG0170L3","88"),("GG0170M3","88"),
                        ("GG0170P3","88"),("GG0170Q3","0")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
    except Exception as e:
        print("DCO FABG autofill error:", e)

def dco_fill_bladder_and_bowel(driver, wait):
    try:
        for fld,val in [("M1600_UTI","00"),("M1620_BWL_INCONT","00")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
        try:
            driver.find_element(By.ID, "9808").send_keys("Vietnamese")
        except: pass
    except Exception as e:
        print("DCO Bladder&Bowel autofill error:", e)

def dco_fill_health_conditions(driver, wait):
    try:
        if dd := wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='J0510']"))):
            Select(dd).select_by_value("0")
        for cb_id in [
            "12804","12807","12818","12816","12814","12990","12983","12980",
            "12981","12979","12974","12978","12971","12964","12962","12960",
            "12993","12997","12999"
        ]:
            try:
                cb = driver.find_element(By.ID, cb_id)
                if not cb.is_selected(): click_element(driver, cb)
            except: pass
        try:
            driver.find_element(By.ID, "12801").send_keys("3/10")
        except: pass
        try:
            driver.find_element(By.ID, "12828").send_keys(
                "Limits functional mobility, such as, bed mobility, transfers, and gait. Can lead to slower progress with PT and impede ability to meet goals."
            )
        except: pass
        for fld in ["J0520","J1800","J1900A"]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']")))
                if fld == "J1900A":
                    Select(dd).select_by_value("0")
                else:
                    Select(dd).select_by_value("2")
            except: pass
        for j in driver.find_elements(By.CSS_SELECTOR, "select[mitemfield='J1900B']"):
            try: Select(j).select_by_value("0")
            except: pass
        for cb_id in ["9453","9458","9459","9465","9471","9475","9463","9485"]:
            try:
                cb = driver.find_element(By.ID, cb_id)
                if not cb.is_selected(): click_element(driver, cb)
            except: pass
        try:
            driver.find_element(By.ID, "9452").send_keys("18")
        except: pass
        for tid in ["9490","9491","9492","9493","9494","9495"]:
            try: driver.find_element(By.ID, tid).send_keys("Clear")
            except: pass
        for cb_id in ["9582","9583"]:
            try:
                cb = driver.find_element(By.ID, cb_id)
                if not cb.is_selected(): click_element(driver, cb)
            except: pass
    except Exception as e:
        print("DCO Health Conditions autofill error:", e)

def dco_fill_swallowing_nutritional_status(driver, wait):
    try:
        for mitem in ["AdvanceDirectives_6","AdvanceDirectives_3"]:
            try:
                cb = driver.find_element(By.CSS_SELECTOR, f"input[mitemfield='{mitem}']")
                if not cb.is_selected(): click_element(driver, cb)
            except: pass
        for cb_id in ["K0520Z4","K0520Z5"]:
            try:
                cb = driver.find_element(By.ID, cb_id)
                if not cb.is_selected(): click_element(driver, cb)
            except: pass
        try:
            Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M1870_CUR_FEEDING']")))).select_by_value("01")
        except: pass
        for tid in [
            "10977","10978","10979","10980","10981","10982","10983","10984","10985","10987",
            "10986","10988","10989","10990","10991","10992","10993","10994","10995","10996",
            "10997","10998","10999","11000","11001","11002"
        ]:
            try: driver.find_element(By.ID, tid).send_keys("3+")
            except: pass
        for tid in [
            "11003","11004","11005","11006","11007","11008","11009","11010","11011","11012","11013","11014","11015"
        ]:
            try: driver.find_element(By.ID, tid).send_keys("WNL")
            except: pass
        for tid in [
            "11029","11043","11044","11045","11046","11047","11048","11050","11049","11053",
            "11052","11054","11051"
        ]:
            try: driver.find_element(By.ID, tid).send_keys("WNL")
            except: pass
    except Exception as e:
        print("DCO Swallowing/Nutritional autofill error:", e)

def dco_fill_skin_conditions(driver, wait):
    try:
        for fld,val in [("M1306_UNHLD_STG2_PRSR_ULCR","0"),("M1324_STG_PRBLM_ULCER","NA"),
                        ("M1330_STAS_ULCR_PRSNT","00"),("M1340_SRGCL_WND_PRSNT","00")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
    except Exception as e:
        print("DCO Skin Conditions autofill error:", e)

def dco_fill_medications(driver, wait):
    try:
        cb = wait.until(EC.presence_of_element_located((By.ID, "N0415Z1")))
        if not cb.is_selected(): click_element(driver, cb)
        dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M2004_MDCTN_INTRVTN']"))); Select(dd).select_by_value("9")
        dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[mitemfield='M2020_CRNT_MGMT_ORAL_MDCTN']"))); Select(dd).select_by_value("02")
    except Exception as e:
        print("DCO Medications autofill error:", e)

def dco_fill_special_treatment_procedures_and_programs(driver, wait):
    try:
        el = wait.until(EC.element_to_be_clickable((By.ID, "O0110Z1C")));
        if not el.is_selected(): click_element(driver, el)
        for fld,val in [("O0350","0"),("M1040_INFLNZ_RCVD_AGNCY","0")]:
            try:
                dd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"select[mitemfield='{fld}']"))); Select(dd).select_by_value(val)
            except: pass
    except Exception as e:
        print("DCO Special Treatment autofill error:", e)

def dco_fill_participation_goal_setting(driver, wait):
    try:
        for mmodel in [
            "M2400_INTRVTN_SMRY_FALL_PRVNT",
            "M2400_INTRVTN_SMRY_DPRSN",
            "M2400_INTRVTN_SMRY_PAIN_MNTR",
            "M2400_INTRVTN_SMRY_PRSULC_PRVN",
            "M2400_INTRVTN_SMRY_PRSULC_WET"
        ]:
            try:
                cb = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"input[ng-model='oasis.oasisDetails.{mmodel}']")))
                if not cb.is_selected(): click_element(driver, cb)
            except: pass
    except Exception as e:
        print("DCO Participation/Goal autofill error:", e)

# ========== FLASK APP & GUI ==========
app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>PT Selenium Autofill</title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
    h1,h2 { margin-top: 1em; }
    .section { margin-bottom: 2em; }
    button { margin: 0.2em; padding: 0.5em 1em; }
  </style>
</head>
<body>
  <h1>PT Selenium Autofill</h1>
  <p><strong>Expiration:</strong> {{ expiration }}</p>
  <div>
    <button onclick="launch()">🔍 Open / Bring Forward Browser</button>
    <button onclick="quit()">❌ Quit Browser</button>
    <span id="status" style="margin-left: 1em; color: green;"></span>
  </div>

  <div class="section">
    <h2>SOC Autofill</h2>
    {% for name, func in soc %}
      <button onclick="autofill('soc', {{ loop.index0 }})">{{ name }}</button>
    {% endfor %}
  </div>

  <div class="section">
    <h2>RECERT Autofill</h2>
    {% for name, func in recert %}
      <button onclick="autofill('recert', {{ loop.index0 }})">{{ name }}</button>
    {% endfor %}
  </div>

  <div class="section">
    <h2>DCO Autofill</h2>
    {% for name, func in dco %}
      <button onclick="autofill('dco', {{ loop.index0 }})">{{ name }}</button>
    {% endfor %}
  </div>

  <script>
    function launch() {
      fetch('/launch', { method: 'POST' })
        .then(res => res.json()).then(j => showStatus(j.status));
    }
    function quit() {
      fetch('/quit', { method: 'POST' })
        .then(res => res.json()).then(j => showStatus(j.status));
    }
    function autofill(tab, idx) {
      showStatus('Running ' + tab.toUpperCase() + ' #' + idx + ' ...');
      fetch(`/autofill/${tab}/${idx}`, { method: 'POST' })
        .then(res => res.json())
        .then(j => showStatus(j.status))
        .catch(err => showStatus('Error: ' + err));
    }
    function showStatus(msg) {
      const s = document.getElementById('status');
      s.textContent = msg;
      setTimeout(() => { s.textContent = '' }, 5000);
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML,
        expiration=EXPIRATION_DATE.strftime("%b %d, %Y"),
        soc=[(name, func) for name, func in [
            ("Administrative Info", autofill_administrative),
            ("Hearing/Speech/Vision", fill_hearing_speech_vision),
            ("Cognitive Patterns", fill_cognitive_patterns),
            ("Mood", fill_mood),
            ("Behavior", fill_behavior),
            ("Preferences", fill_preferences),
            ("Functional Status", fill_functional_status),
            ("Functional Abilities & Goals", fill_functional_abilities_and_goals),
            ("Bladder and Bowel", fill_bladder_and_bowel),
            ("Active Diagnoses", fill_active_diagnoses),
            ("Health Conditions", fill_health_conditions),
            ("Swallowing/Nutritional Status", fill_swallowing_nutritional_status),
            ("Skin Conditions", fill_skin_conditions),
            ("Medications", fill_medications),
            ("Special Treatment/Procedures/Programs", fill_special_treatment)
        ]],
        recert=[(name, func) for name, func in [
            ("Administrative Info", recert_autofill_administrative),
            ("Functional Status", recert_fill_functional_status),
            ("Functional Abilities & Goals", recert_fill_functional_abilities_and_goals),
            ("Health Conditions", recert_fill_health_conditions),
            ("Skin Conditions", recert_fill_skin_conditions),
            ("Active Diagnoses", recert_fill_active_diagnoses),
        ]],
        dco=[(name, func) for name, func in [
            ("Administrative Info", dco_autofill_administrative),
            ("Hearing/Speech/Vision", dco_fill_hearing_speech_vision),
            ("Cognitive Patterns", dco_fill_cognitive_patterns),
            ("Mood", dco_fill_mood),
            ("Behavior", dco_fill_behavior),
            ("Preferences", dco_fill_preferences),
            ("Functional Status", dco_fill_functional_status),
            ("Functional Abilities & Goals", dco_fill_functional_abilities_and_goals),
            ("Bladder and Bowel", dco_fill_bladder_and_bowel),
            ("Health Conditions", dco_fill_health_conditions),
            ("Swallowing/Nutritional Status", dco_fill_swallowing_nutritional_status),
            ("Skin Conditions", dco_fill_skin_conditions),
            ("Medications", dco_fill_medications),
            ("Special Treatment/Procedures/Programs", dco_fill_special_treatment_procedures_and_programs),
            ("Participation/Goal Setting", dco_fill_participation_goal_setting),
        ]]
    )

@app.route("/launch", methods=["POST"])
def launch_browser():
    threading.Thread(target=browser_manager.launch).start()
    return jsonify(status="Launching browser...")

@app.route("/quit", methods=["POST"])
def quit_browser():
    browser_manager.quit()
    return jsonify(status="Browser closed.")

@app.route("/autofill/<tab>/<int:idx>", methods=["POST"])
def autofill(tab, idx):
    driver = browser_manager.driver
    wait = browser_manager.wait
    if not driver:
        return jsonify(status="Please open the browser first."), 400

    mapping = {
        "soc": [
            autofill_administrative, fill_hearing_speech_vision, fill_cognitive_patterns,
            fill_mood, fill_behavior, fill_preferences, fill_functional_status,
            fill_functional_abilities_and_goals, fill_bladder_and_bowel,
            fill_active_diagnoses, fill_health_conditions,
            fill_swallowing_nutritional_status, fill_skin_conditions,
            fill_medications, fill_special_treatment
        ],
        "recert": [
            recert_autofill_administrative, recert_fill_functional_status,
            recert_fill_functional_abilities_and_goals,
            recert_fill_health_conditions, recert_fill_skin_conditions,
            recert_fill_active_diagnoses
        ],
        "dco": [
            dco_autofill_administrative, dco_fill_hearing_speech_vision,
            dco_fill_cognitive_patterns, dco_fill_mood, dco_fill_behavior,
            dco_fill_preferences, dco_fill_functional_status,
            dco_fill_functional_abilities_and_goals,
            dco_fill_bladder_and_bowel, dco_fill_health_conditions,
            dco_fill_swallowing_nutritional_status,
            dco_fill_skin_conditions, dco_fill_medications,
            dco_fill_special_treatment_procedures_and_programs,
            dco_fill_participation_goal_setting
        ]
    }.get(tab, [])

    if idx < 0 or idx >= len(mapping):
        return jsonify(status="Invalid section index."), 400

    func = mapping[idx]
    threading.Thread(target=lambda: func(driver, wait)).start()
    return jsonify(status=f"Triggered {tab.upper()} section #{idx}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
