import pandas as pd
import numpy as np
import streamlit as st

def read_file(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        df = pd.read_excel(uploaded_file)
    return df


def clean_email(df, email_col):
    return df[email_col].str.strip().str.lower()


def clean_phone(df, phone_col):
    return (df[phone_col]
            .str.strip()
            .str.replace("/D", "", regex=True)
            .str.replace("^62", "0", regex=True)
            .str.replace("^8", "08", regex=True)
            )


def clean_df_hub(df):
    return (df
        .rename(columns=lambda c: c.lower().replace(" ", "_"))
        .assign(
            email=lambda df_: clean_email(df_, "email"),
            phone_number=lambda df_: clean_phone(df_, "phone_number"),
        )
        .loc[lambda df_: (df_["email"] != np.nan) & (df_["phone_number"] != np.nan)]
        .drop_duplicates(subset=["email"])
        .drop_duplicates(subset=["phone_number"])
        .dropna(subset=["phone_number"])
        .dropna(subset=["email"])
    )


def clean_df_er(df):
    map_stage = {
        "Appointment": "Sales qualified lead",
        "Show": "Opportunity",
        "Down Payment": "Customer",
        "Fully Paid": "Customer",
        "False": "Lead",
        "Lead": "Lead",
        np.nan: "Lead",
    }
    map_lp = {
        "Ya": "Yes",
        "Mau!": "Yes",
        "Tidak": "No",
        "Engga, deh.": "No",
        np.nan: "Blank",
    }
    return (df
        .rename(columns=lambda c: c.lower().replace(" ", "_").replace("/", "_").replace("?", ""))
        .rename(columns={
            "stage_display_name": "stage",
            "source_type": "source",
            "phone_number": "phone",
        })
        .loc[
            lambda df_: 
                (df_["source"].isin(["Digital-Paid", "Digital-Organic"])) &\
                (df_["stage"] != "Renewal") &\
                (df_["email"] != np.nan) &\
                (df_["phone"] != np.nan)
        ]
        .assign(
            email=lambda df_: clean_email(df_, "email"),
            phone=lambda df_: clean_phone(df_, "phone"),
            stage=lambda df_: df_["stage"].map(map_stage),
            learning_preference=lambda df_: df_["learning_preference"].map(map_lp),
            tmk_call=lambda df_: df_["tmk_call"].map({True: 1, False: 0})
        )
        .drop_duplicates(subset=["email"])
        .drop_duplicates(subset=["phone"])
        .dropna(subset=["email"])
        .dropna(subset=["phone"])
    )


def merge_dfs(df_hub_clean, df_er_clean):
    df_merge_email = (df_hub_clean
        .merge(
            df_er_clean, 
            how="inner", 
            left_on="email", 
            right_on="email", 
            validate="one_to_one"
        )
        .loc[:, ["record_id", "phone_number", "email", "stage", "learning_preference", "tmk_call"]]
        )

    df_merge_phone = (df_hub_clean
        .loc[~df_hub_clean["email"].isin(df_merge_email["email"])]
        .merge(
            df_er_clean, 
            how="inner", 
            left_on="phone_number", 
            right_on="phone", 
            validate="one_to_one"
        )
        .loc[:, ["record_id", "phone_number", "email_x", "stage", "learning_preference", "tmk_call"]]
        .rename(columns={"email_x": "email"})
    )
    return pd.concat([df_merge_email, df_merge_phone], axis=0)


def get_result(df_merged, df_er_clean):
    df_match = (df_merged
        .dropna(subset=["stage", "learning_preference", "tmk_call"])
        .rename(columns=lambda c:(c
                                .title()
                                .replace("_", " ")
                                .replace("Id", "ID")
                                .replace("Stage", "Lifecycle Stage")
                                .replace("Tmk Call", "Is TMK Call?")
                                ))
    )
    df_no_match = (df_er_clean
        .loc[
            ~(df_er_clean["email"].isin(df_match["Email"])) &\
            ~(df_er_clean["phone"].isin(df_match["Phone Number"])), 
            ["email", "phone", "stage", "learning_preference", "tmk_call"]
        ]
        .rename(columns=lambda c:(c
                                .title()
                                .replace("_", " ")
                                .replace("Id", "ID")
                                .replace("Stage", "Lifecycle Stage")
                                .replace("Tmk Call", "Is TMK Call?")
                                ))
    )
    return df_match, df_no_match

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')