import asyncio
import json
import aiohttp

# Your list of logins mapping username_prefix:uid
LOGINS_DATA = [
    "muhammadsodiq2013:427ddcfb-4d12-4858-66b6-08deafe01240",
    "salohiddin2013:c1c11a90-3018-45f4-0b48-08de8f003f92",
    "sevinch2013:6acc6b49-a685-4098-6d01-08de72e91a36",
    "mehriniso2013:3d26c9bb-2a72-4e48-3097-08deb26b7cfc",
    "shoxjaxon2013:76515684-7001-4878-6b85-08deafe01240",
    "zilolaxon2013:68124a45-1740-4c26-8570-08de72e91a36"
]

URL = "https://api.aistudy.uz/api/StudyAILms/Account/UserRegisteration"
PASSWORD = "12345678a"
OUTPUT_FILE = "successful_logins.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=0"
}

successful_accounts = []
file_lock = asyncio.Lock()

async def save_success(account_string):
    """Safely appends to the list and rewrites the text file as a structured array string."""
    async with file_lock:
        successful_accounts.append(account_string)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(successful_accounts))

async def register_single_user(session, semaphore, username_prefix, uid):
    async with semaphore:
        # Fixed: Just build the correct final name directly
        target_username = f"{username_prefix}14m"
        
        # Static inputs updated for testing configuration
        verification_code = 588308
        recaptcha_token = "0cAFcWeA5KAZY8Mk7gHtM3XWioMy_Or_18mYa0dy9_SNLF_K0UqXR6ftnmAdADKizpLBWhIB6dGClBp0UQeioYCwtNHF3Xb-UqOQaUGqSAu9qoKKEZW7S9wXpMVQqMCWxl8FvfaXa_EuXBI7FncREHUv0BV942kQ8J6CHv5Z_oRV_MzD8c3pPi1zxgwgDST6SZiZxmSIb_bHytSa1PilQwjyNkSWXtuD1_JXGNIGAjv-yQTrvpGs1uHUiqaDQhlSQO0vj9aEPWku7YPi99O2xu_tr9tgC3fIYOYb-Fd3XKMJVwYM1pnmlfWprOcl4u79nO_ju9sS4QCqGofRlUZueHP53taUb9r6bEJqiQcdx1lu_QOG9WCoOO48oulw7GkhIyUyLAFARtnpaUAQ4yuy-SxUUgr1DwZZs7UCs58dt8fux7z7VQk25Mhcq5kBvypo1P7N4I9O9ecGFelks3CW2ZIZP-xtAMkruCZG8Tqa3Wh7dkuPUcc1eEe6Ak5TiQ2GgkbEFJYSbN-Q5BJvCyOwgoZ6oAdusFLcS3cPdIhUYGbXQzvRnP9RaQpmTETR-n1n7dfSrwu-N3DP1rTk7kRY4INY2JLihhCR2mWyJosCj4d4-4aSVtVa3LWLoqb1BBD5ZI_1MkyIx9ykCkDuALfso0tCdYZ3GoNUD8FIG-I12nTS1jzli6kXk_oYAYssdftwSOgNG2GYTvsa4AbFdf66kDpXWARUidFCLFMv0d6NafG-nWskDHoeiC_pkiPNU-0oHWZB_NAYUcjS9pYQpbEftIgfwECVqbqU8dx6W-SFlYRQAeKDgidKLiJg4_fkL60-joe1UhdWpxThw0U0NLm6EjTvdzxGEptObiQ6DLDEXXwFZUun-luOoHGOjoRoZZje6KHF0Wz8pT7-3ilLWoZY2CaA7hYc9dmjQC1GVZgp_jRioAhpaOLBlIBLjatUEJmFx7d6o5RKn13QeojHxRYom_SWlgEh2r_bqy1zeYcevzKuyAoE4NmfRyunwRP5b-H9WtqRTOc6Y1xEVHC_Jy5xbYVaoqLcPHmOk3h2efgIoEYQ8422mv1_nvgO3nC8Pcp2iSkrR1pz0U6e-dEoHWvWEeNrdcw-Ifz13ZtNBZbmW1BnqaPqn3yyYv_S_qAWnVBeMxZZeElmD1t_B82U8SI2-QT9c_mKlPvi_4F_dXn-wvyKvjwp69sd_h6wANT-TkBOwx1XjC1RCwKyJNj2DwPV735EoeBv3VQEzqrdV38cG5OsrHKuaTyNYAhpTXlqzdhLa6OaNLGmdDxV0o0DfO9K2-KssQWEjTfUslVakY2H-8XzxD2A6nHrkz9IC0gtWTddA_rMXxl1ZSyIdJqp7AVd2C1DHEDBCTpTddCVyOCD02jX5DlzPUwEzBxWCPYwY5NYyLFfpr_iXaBXbR7qcCbr7iP1Irfb0YmFkXU4D6vEW_SiePlYO-FpMSp0hL7OoopYQtLUIu-ZIgXGLUAP-8G4QZIws3LyGaWV2O3Iyv3TzAHAc-1RjXsWCMSOlUdbHMyuwHj5N6ifdEQ2F5IiJQzJ9udbWY02sh88C2qGstNWIk4CEgtS_MrXsSsFZhLYXucrklv3bOiHxK_b63F8103CcDpew7iqN4WayHHSd63tkYd4Z_UHt56TzE7wCaJ1b_yE-WxDubOXCmBo7M0vb_S0f1MbAmVjaYHGs12KPMmZW-43CT9R-BXixl_3HHGw5S6I7QW30qecvsRjDbHI2Z1BFeAX_zq04Y_rj5AZcTE7WGeYsMb4_m1sauV1DJk81BHaWQQI95KyBZ2xANtzyHLsEBAzxKGrwfcxYJvjjB6eYQPI3ngaszZPLwMUKm4L1swhDxGPx0G1dkPFIC7XxoXu50-S9zVOHLZCFBnFrpvzPQzfOiVcg0RJVTBLvSNCokXrCfquJ2jXu1lucl1Gv8YQ1luKTXXr0GzcK-VzjKNiTmeKuZEuXwOxqf25pjXnb3zH2r5hFxNaoWfeaxp57rrlH6pxKzHiTYG1_FE1miqwUBpKlF11-YaoV9yRN8JAQC71NEK8pPjw3xLEAWOU1a-PCaSBpd5Rq70vfqo5vBMGUB7omIgHob395GaB81Zx1b0_mLRmgtMvwY0-ZS_99hg1xd83kFIiW-pdUKM8M7MS-341T8bWMGfrjpOdg0KMjkeY09bIpSSG3m_HVb55UsQt-DmlgWdlnuQuYOQJaQsD1MdfGJ2roWgV7oSJWQFTIWTHDFhIW1JcfupYMh0HjY_xwbSGgBN998ClLzOeVgWyNgwvTSo_PsePMiNLQ"

        # Fixed: Explicitly convert username and numerical parameters into string objects
        payload = {
            "uid": str(uid),
            "username": str(target_username),
            "password": str(PASSWORD),
            "confirmPassword": str(PASSWORD),
            "verificationCode": str(verification_code),
            "recaptchaToken": str(recaptcha_token)
        }

        print(f"-> Sending request for {target_username}...")
        try:
            async with session.post(URL, headers=HEADERS, json=payload) as response:
                status = response.status
                text = await response.text()
                
                print(f"[Result] {target_username} | Status: {status}")
                
                if status == 200:
                    account_format = f"{target_username}:{PASSWORD}"
                    await save_success(account_format)
                    print(f" Saved to {OUTPUT_FILE} -> {account_format}")
                else:
                    try:
                        parsed_json = json.loads(text)
                        print(f"Response Error Body: {json.dumps(parsed_json, ensure_ascii=False)}")
                    except json.JSONDecodeError:
                        print(f"Response Raw: {text}")
                        
        except Exception as e:
            print(f"[Error] Failed to request {target_username}: {e}")

async def main():
    sem = asyncio.Semaphore(1)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("[]")
        
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in LOGINS_DATA:
            if ":" in item:
                prefix, uid = item.split(":", 1)
                task = asyncio.create_task(register_single_user(session, sem, prefix, uid))
                tasks.append(task)
        
        await asyncio.gather(*tasks)
        print(f"\nExecution Complete. Final results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())