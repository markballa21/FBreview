import streamlit as st
from google import genai
import trafilatura

# הגדרת ה-Client של Gemini
# מומלץ להגדיר את GEMINI_API_KEY במשתני סביבה או ב-secrets של Streamlit
client = genai.Client(api_key="AQ.Ab8RN6IR_wGVphMmu9ryKwJt58f4ZdK3qis7ScDwXJnJ3k0pKg")

# טעינת קובץ המדיניות החיצוני
def load_policy():
    try:
        with open("meta_policy.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "שגיאה: קובץ המדיניות meta_policy.txt לא נמצא."

FB_POLICY_CONTEXT = load_policy()

st.set_page_config(page_title="סורק מדיניות פייסבוק", layout="wide")
st.title("🛡️ סורק דפי נחיתה למדיניות מטא (Gemini Pro)")

url_input = st.text_input("הזן קישור לדף הנחיתה לבדיקה:", placeholder="https://example.com/landing-page")

if st.button("🚀 נתח דף נחיתה", type="primary"):
    if not url_input.startswith("http"):
        st.warning("נא להזין קישור תקין הכולל http:// או https://")
    else:
        with st.spinner("סורק את הדף ומבצע ניתוח מול מדיניות פייסבוק..."):
            # 1. חילוץ התוכן מהקישור
            downloaded = trafilatura.fetch_url(url_input)
            page_text = trafilatura.extract(downloaded)

            if not page_text:
                st.error("לא ניתן היה לקרוא את תוכן הדף. ודא שהאתר פתוח לגישה ציבורית.")
            else:
                # 2. הרכבת הפרומפט לסוכן הבדיקה
                prompt = f"""
                אתה מומחה בכיר לעמידה במדיניות הפרסום של מטא (Meta / Facebook Ads Policy).

                להלן תקציר המדיניות:
                {FB_POLICY_CONTEXT}

                להלן התוכן המלא שחולץ מדף הנחיתה:
                ---
                {page_text}
                ---

                בצע בדיקה מעמיקה והחזר דוח מובנה הכולל:
                1. **ציון סיכון כללי (Risk Score):** נמוך / בינוני / גבוה (עם הסבר קצר של שורה אחת).
                2. **פירוט הפרות (Violations Found):** 
                   - ציטוט מדויק מהדף שעלול להיפסל.
                   - איזה סעיף מדיניות הוא מפר ומדוע.
                3. **הצעות לתיקון ושכתוב (Compliant Copy):** לכל הפרה, הצע חלופה שיווקית חזקה שממירה היטב אך אינה מפרה את הכללים.
                4. **המלצות נוספות לשיפור הדף.**

                עצב את התשובה בעברית, ב-Markdown ברור וקריא עם טבלאות והדגשות.
                """

                try:
                    # 3. קריאה למודל
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                    report = response.text

                    # 4. הצגת הדוח
                    st.markdown("---")
                    st.markdown(report)

                    # כפתור הורדת הדוח
                    st.download_button(
                        label="📥 הורד דוח כקובץ Markdown",
                        data=report,
                        file_name="facebook_policy_audit.md",
                        mime="text/markdown"
                    )

                except Exception as e:
                    st.error(f"שגיאה בעת הפעלת המודל: {e}")