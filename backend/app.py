import streamlit as st
import requests
import pandas as pd

st.title("Talk to Data 📊")

question = st.text_input("Ask your question")

if st.button("Run Query"):
    if question.strip():
        try:
            res = requests.post(
                "http://127.0.0.1:8000/query",
                json={"question": question}
            )

            data = res.json()

            # ✅ SAFE CHECK
            if "answer" in data:
                st.write(data["answer"])
            elif "result" in data:
                result = data["result"]
                # ✅ HANDLE RESULT TYPES
                if result["type"] == "metric":
                    st.metric(result["label"], result["value"])
                elif result["type"] == "chart":
                    df = pd.DataFrame({
                        "label": result["labels"],
                        "value": result["values"]
                    })
                    st.bar_chart(df.set_index("label"))
                elif result["type"] == "table":
                    df = pd.DataFrame(result["rows"])
                    st.dataframe(df)
                else:
                    st.warning("Unknown result type")
            else:
                st.error(f"Backend error: {data}")
                st.stop()

        except Exception as e:
            st.error(f"Error: {e}")
