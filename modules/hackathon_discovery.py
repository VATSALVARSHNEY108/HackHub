author="Vatsal Varshney"
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from utils.scraper import HackathonScraper
from utils.filters import HackathonFilter
from utils.data_exporter import DataExporter


def render():
    st.header("🔍 Hackathon Discovery")
    st.markdown("Discover and explore hackathons from multiple sources worldwide!")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Discover", "🔍 Browse & Filter", "📊 Analytics", "📥 Export"])

    with tab1:
        render_discovery()

    with tab2:
        render_browse_filter()

    with tab3:
        render_analytics()

    with tab4:
        render_export()


def render_discovery():
    st.subheader("🚀 Discover Hackathons")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Find the perfect hackathon for your skills and interests!**

        Our discovery engine searches across multiple platforms including:
        - 🌟 Devpost
        - 🎯 Hackathon.io  
        - 🏆 HackerEarth
        """)

    with col2:
        if st.button("🔍 Search Hackathons", type="primary", use_container_width=True):
            search_hackathons()

        if st.button("🔄 Refresh Data", use_container_width=True):
            refresh_hackathon_data()

    # Display current data stats
    if st.session_state.hackathons_data:
        st.success(f"✅ Found {len(st.session_state.hackathons_data)} hackathons!")

        # Quick preview
        st.markdown("### 👀 Recent Discoveries")
        preview_df = pd.DataFrame(st.session_state.hackathons_data[:5])
        if not preview_df.empty:
            st.dataframe(
                preview_df[['title', 'date', 'location', 'source']],
                use_container_width=True
            )
    else:
        st.info("Click 'Search Hackathons' to discover events!")


def render_browse_filter():
    st.subheader("🔍 Browse & Filter Hackathons")

    if not st.session_state.hackathons_data:
        st.info("No hackathon data available. Please discover hackathons first!")
        return

    # Create filter instance
    hackathon_filter = HackathonFilter(st.session_state.hackathons_data)

    # Filter controls
    st.markdown("### 🎛️ Filter Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Text search
        search_term = st.text_input("🔍 Search", placeholder="Search titles, descriptions, tags...")

        # Date range
        st.markdown("**📅 Date Range**")
        start_date = st.date_input("From", value=date.today())
        end_date = st.date_input("To")

    with col2:
        # Location filters
        location_type = st.selectbox(
            "📍 Location Type",
            ["", "Online", "In-person", "Hybrid"]
        )

        location_name = st.text_input("🌍 Location", placeholder="City, Country...")

    with col3:
        # Source and tags
        available_sources = list(set([h.get('source', '') for h in st.session_state.hackathons_data]))
        sources = st.multiselect("📱 Sources", available_sources)

        # Extract all unique tags
        all_tags = set()
        for h in st.session_state.hackathons_data:
            if isinstance(h.get('tags'), list):
                all_tags.update(h['tags'])

        tags = st.multiselect("🏷️ Tags", sorted(list(all_tags)))

    # Apply filters
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Apply Filters", type="primary"):
            apply_filters(hackathon_filter, search_term, start_date, end_date,
                          location_type, location_name, sources, tags)

    with col2:
        show_upcoming_only = st.checkbox("📅 Upcoming only", value=True)

    # Apply upcoming filter if selected
    if show_upcoming_only:
        hackathon_filter.filter_upcoming_only()

    # Display filtered results
    filtered_data = hackathon_filter.get_results()
    stats = hackathon_filter.get_stats()

    st.markdown(f"### 📋 Results ({stats['filtered_count']} of {stats['original_count']} hackathons)")

    if stats['applied_filters']:
        st.markdown("**Active filters:** " + " | ".join(stats['applied_filters']))

    # Display hackathons
    for hackathon in filtered_data:
        with st.expander(f"🚀 {hackathon['title']} - {hackathon.get('date', 'TBD')}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Description:** {hackathon.get('description', 'No description available')}")
                st.markdown(
                    f"**Location:** {hackathon.get('location', 'TBD')} ({hackathon.get('location_type', 'Unknown')})")

                if hackathon.get('tags'):
                    tags_str = ", ".join(hackathon['tags'])
                    st.markdown(f"**Tags:** {tags_str}")

                if hackathon.get('prize'):
                    st.markdown(f"**Prize:** {hackathon['prize']}")

            with col2:
                st.markdown(f"**Source:** {hackathon.get('source', 'Unknown')}")
                if hackathon.get('url'):
                    st.markdown(f"[🔗 View Details]({hackathon['url']})")


def render_analytics():
    st.subheader("📊 Hackathon Analytics")

    if not st.session_state.hackathons_data:
        st.info("No data available for analytics. Please discover hackathons first!")
        return

    df = pd.DataFrame(st.session_state.hackathons_data)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Hackathons", len(df))

    with col2:
        online_count = len(df[df['location_type'] == 'Online'])
        st.metric("Online Events", online_count)

    with col3:
        inperson_count = len(df[df['location_type'] == 'In-person'])
        st.metric("In-person Events", inperson_count)

    with col4:
        hybrid_count = len(df[df['location_type'] == 'Hybrid'])
        st.metric("Hybrid Events", hybrid_count)

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Location type distribution
        location_counts = df['location_type'].value_counts()
        fig_location = px.pie(
            values=location_counts.values,
            names=location_counts.index,
            title="Events by Location Type"
        )
        st.plotly_chart(fig_location, use_container_width=True)

    with col2:
        # Source distribution
        source_counts = df['source'].value_counts()
        fig_source = px.bar(
            x=source_counts.values,
            y=source_counts.index,
            orientation='h',
            title="Events by Source"
        )
        st.plotly_chart(fig_source, use_container_width=True)

    # Timeline analysis
    if 'date' in df.columns:
        st.markdown("### 📅 Timeline Analysis")

        # Convert dates and create timeline
        df_timeline = df.copy()
        df_timeline['date'] = pd.to_datetime(df_timeline['date'], errors='coerce')
        df_timeline = df_timeline.dropna(subset=['date'])

        if not df_timeline.empty:
            df_timeline['month'] = df_timeline['date'].dt.to_period('M')
            monthly_counts = df_timeline['month'].value_counts().sort_index()

            fig_timeline = px.line(
                x=monthly_counts.index.astype(str),
                y=monthly_counts.values,
                title="Hackathons Over Time",
                labels={'x': 'Month', 'y': 'Number of Events'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)


def render_export():
    st.subheader("📥 Export Data")

    if not st.session_state.hackathons_data:
        st.info("No data available for export. Please discover hackathons first!")
        return

    st.markdown(f"**{len(st.session_state.hackathons_data)} hackathons** ready for export")

    exporter = DataExporter()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Export to CSV", use_container_width=True):
            try:
                filename = exporter.export_to_csv(st.session_state.hackathons_data)
                st.success(f"✅ Exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

    with col2:
        if st.button("📋 Export to JSON", use_container_width=True):
            try:
                filename = exporter.export_to_json(st.session_state.hackathons_data)
                st.success(f"✅ Exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

    with col3:
        if st.button("📊 Export to Excel", use_container_width=True):
            try:
                filename = exporter.export_to_excel(st.session_state.hackathons_data)
                st.success(f"✅ Exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")


def search_hackathons():
    """Search for hackathons using the scraper"""
    with st.spinner("🔍 Searching hackathons across multiple platforms..."):
        try:
            scraper = HackathonScraper()
            hackathons = scraper.scrape_all()

            if hackathons:
                st.session_state.hackathons_data = hackathons
                st.success(f"✅ Found {len(hackathons)} hackathons!")
            else:
                st.warning("No hackathons found. This might be due to website changes or connectivity issues.")

        except Exception as e:
            st.error(f"Error searching hackathons: {str(e)}")


def refresh_hackathon_data():
    """Refresh hackathon data"""
    st.session_state.hackathons_data = []
    st.success("🔄 Data refreshed! Click 'Search Hackathons' to load new data.")


def apply_filters(hackathon_filter, search_term, start_date, end_date,
                  location_type, location_name, sources, tags):
    """Apply all selected filters"""

    if search_term:
        hackathon_filter.search_text(search_term)

    if start_date or end_date:
        hackathon_filter.filter_by_date_range(
            start_date.isoformat() if start_date else None,
            end_date.isoformat() if end_date else None
        )

    if location_type:
        hackathon_filter.filter_by_location_type(location_type)

    if location_name:
        hackathon_filter.filter_by_location_name(location_name)

    if sources:
        hackathon_filter.filter_by_source(sources)

    if tags:
        hackathon_filter.filter_by_tags(tags)

    return hackathon_filter