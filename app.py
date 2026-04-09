import streamlit as st
import pandas as pd
import json
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="AdVerify Pro", page_icon="🛡️", layout="centered")

# --- 2. THE ENGINE (Professional Classes) ---
class DataSources:
    @staticmethod
    def get_data(location):
        mock_db = {
            "Main St Billboard": {"registry": 500, "live": 550},
            "Downtown Bus Stop": {"registry": 200, "live": 200},
            "Radio Spot (Morning)": {"registry": 150, "live": 140},
            "Instagram Local Feed": {"registry": 50, "live": 120}
        }
        return mock_db.get(location, {"registry": 0, "live": 0})

class AdVerifier:
    def __init__(self, api_key):
        self.api_key = api_key
        self.sources = DataSources()

    def verify(self, location, user_price):
        # --- DEMO BYPASS ---
        if self.api_key == "DEMO":
            time.sleep(1.5) 
            # Logic: If price is > 10% above live, call it overpriced
            live_price = self.sources.get_data(location)['live']
            if user_price > (live_price * 1.1):
                return {
                    "status": "OVERPRICED",
                    "confidence_score": 92,
                    "advice": "DEMO MODE: This quote is significantly above the local market average. Negotiate for a lower rate."
                }
            return {
                "status": "VERIFIED",
                "confidence_score": 98,
                "advice": "DEMO MODE: This price matches local benchmarks perfectly. Proceed with the contract."
            }

        # --- REAL AI LOGIC ---
        data = self.sources.get_data(location)
        context = {
            "location": location,
            "user_claimed_price": user_price,
            "registry_price": data['registry'],
            "live_scraped_price": data['live']
        }

        llm = ChatOpenAI(api_key=self.api_key, model="gpt-4o", temperature=0)
        prompt = ChatPromptTemplate.from_template("""
        Act as an Advertising Auditor. Analyze this:
        - Location: {location} | Quote: ${user_claimed_price}
        - Registry: ${registry_price} | Live: ${live_scraped_price}
        Output ONLY valid JSON: {{"status": "VERIFIED/OVERPRICED/SCAM_RISK", "confidence_score": 0-100, "advice": "string"}}
        """)
        
        chain = prompt | llm | StrOutputParser()
        
        try:
            response_text = chain.invoke(context).strip('`json \n')
            return json.loads(response_text)
        except Exception as e:
            return {"status": "ERROR", "reason": str(e)}

# --- 3. UI INTERFACE (Sidebar) ---
st.sidebar.header("⚙️ Settings")
key_input = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter a real key or 'DEMO' to test.")
st.sidebar.info("Using 'DEMO' allows for testing without an API key.")

# --- 4. MAIN DASHBOARD ---
st.title("🛡️ AdVerify Local")
st.markdown("### AI Market Audit Agent")
st.write("Professional verification of advertising vendor quotes using LLM analysis.")

# Using a form to group inputs
with st.form("audit_form"):
    c1, c2 = st.columns(2)
    with c1: 
        loc = st.selectbox("Ad Space", ["Main St Billboard", "Downtown Bus Stop", "Radio Spot (Morning)", "Instagram Local Feed"])
    with c2: 
        price = st.number_input("Vendor Quote ($)", min_value=0.0, value=500.0)
    
    submitted = st.form_submit_button("🔍 Run Audit")

# --- 5. EXECUTION LOGIC ---
if submitted:
    if not key_input:
        st.error("⚠️ Please enter 'DEMO' or a real API key in the sidebar.")
    else:
        with st.spinner('AI Agent is auditing prices...'):
            # This calls AdVerifier class
            result = AdVerifier(key_input).verify(loc, price)
        
        if result.get("status") == "ERROR":
            st.error(f"Failed: {result.get('reason')}")
        else:
            st.divider()
            
            # Show Visual Status
            if result["status"] == "VERIFIED":
                st.success("✅ PRICE VERIFIED")
                st.balloons()
            elif result["status"] == "OVERPRICED":
                st.warning("⚠️ PRICE IS TOO HIGH")
            else:
                st.error("🚨 POTENTIAL SCAM DETECTED")

            # Metrics Row
            m1, m2, m3 = st.columns(3)
            m1.metric("Confidence", f"{result['confidence_score']}%")
            m2.metric("Market Avg", f"${DataSources.get_data(loc)['live']}")
            m3.metric("Your Quote", f"${price}")
            
            # The "Upsell" Expander
            with st.expander("📝 See Detailed Audit & Negotiation Strategy"):
                st.info(f"🧠 **AI Advice:** {result['advice']}")
                st.write("---")
                st.caption("Detailed report generated by AdVerify AI Engine.")

st.divider()
st.markdown("### 💼 Professional Services")
st.markdown("[📩 **Hire me on Upwork to discuss your custom AI project**](https://www.upwork.com/freelancers/~01b5e8fc2373c391ce?mp_source=share)")


