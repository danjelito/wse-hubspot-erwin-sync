import streamlit as st
import module

# title
st.title("Hubspot - Erwin Merger 1.0 :fire:")
st.markdown("**A web app used to merge the files from Hubspot and Erwin.**")
st.markdown("Visit project repository [*here*](https://github.com/danjelito/wse-hubspot-erwin-sync)")
st.markdown("*Created by Devan on 2023-10-23*")
# st.markdown('*Updated on 2023-08-16*')

# upload file
st.header("Upload File")
file_hub = st.file_uploader("Upload the file from **Hubspot**.")
file_er = st.file_uploader("Upload the file from **Erwin**.")

if file_hub is not None and file_er is not None:

    st.header("Download Result File")
    with st.spinner('Wait for it...'):

        # read file
        df_hub = module.read_file(file_hub)
        df_er = module.read_file(file_er)

        # clean 
        df_hub_clean = module.clean_df_hub(df_hub)
        df_er_clean = module.clean_df_er(df_er)

        # merge
        df_merge = module.merge_dfs(df_hub_clean, df_er_clean)

        # get result
        df_match, df_no_match = module.get_result(df_merge, df_er_clean)

        # download button
        df_match_csv = module.convert_df(df_match)
        df_no_match_csv = module.convert_df(df_no_match)

    # df match
    st.download_button(
        label= "Match leads",
        data= df_match_csv,
        file_name= "match_data.csv",
    )

    # df no match
    st.download_button(
        label= "No match leads",
        data= df_no_match_csv,
        file_name= "no_match_data.csv",
    )
       
    st.success('Your file is ready to download.', icon="✅")
    st.caption('Note: This is the resulting file. Download and open it with Excel.')
        