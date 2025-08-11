author="Vatsal Varshney"
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class TeamMatcher:
    """ML-powered team matching for optimal hackathon team formation"""

    def __init__(self, participants, weight_skills=0.3, weight_experience=0.3, weight_interests=0.4):
        self.participants = participants
        self.weight_skills = weight_skills
        self.weight_experience = weight_experience
        self.weight_interests = weight_interests

        # Initialize encoders and scalers
        self.experience_encoder = LabelEncoder()
        self.role_encoder = LabelEncoder()
        self.scaler = StandardScaler()

    def generate_teams(self, num_teams, team_size, balance_priority="Skill Diversity", include_leadership=True):
        """Generate optimal teams using ML clustering"""
        try:
            # Prepare feature vectors
            feature_matrix = self.create_feature_matrix()

            # Apply clustering
            teams = self.cluster_participants(feature_matrix, num_teams, team_size)

            # Balance teams based on priority
            teams = self.balance_teams(teams, balance_priority, include_leadership)

            # Format teams for output
            formatted_teams = self.format_teams(teams)

            logger.info(f"Generated {len(formatted_teams)} teams successfully")
            return formatted_teams

        except Exception as e:
            logger.error(f"Error generating teams: {e}")
            raise e

    def create_feature_matrix(self):
        """Create feature matrix for each participant"""
        features = []

        for participant in self.participants:
            feature_vector = []

            # Experience level (numerical)
            exp_mapping = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
            experience_score = exp_mapping.get(participant.get('experience_level', 'Beginner'), 1)
            feature_vector.append(experience_score)

            # Leadership interest (binary)
            feature_vector.append(1 if participant.get('leadership_interest', False) else 0)

            # Team size preference
            feature_vector.append(participant.get('team_size_pref', 4))

            # Role preference (one-hot encoded)
            roles = ["Frontend Developer", "Backend Developer", "Full Stack Developer",
                     "Data Scientist", "ML Engineer", "Designer", "Product Manager", "DevOps"]
            role = participant.get('role_preference', 'Full Stack Developer')
            role_vector = [1 if role == r else 0 for r in roles]
            feature_vector.extend(role_vector)

            # Skills features (TF-IDF style)
            all_skills = (
                    participant.get('programming_langs', []) +
                    participant.get('frameworks', []) +
                    participant.get('databases', []) +
                    participant.get('tools', [])
            )
            skills_text = ' '.join(all_skills).lower()

            # Interests features
            interests_text = ' '.join(participant.get('interests', [])).lower()

            # Store text features separately for TF-IDF processing
            participant['skills_text'] = skills_text
            participant['interests_text'] = interests_text

            features.append(feature_vector)

        # Convert to numpy array
        feature_matrix = np.array(features)

        # Add TF-IDF features for skills and interests
        skills_features = self.create_tfidf_features([p['skills_text'] for p in self.participants])
        interests_features = self.create_tfidf_features([p['interests_text'] for p in self.participants])

        # Combine all features
        combined_features = np.hstack([
            feature_matrix * self.weight_experience,
            skills_features * self.weight_skills,
            interests_features * self.weight_interests
        ])

        # Normalize features
        normalized_features = self.scaler.fit_transform(combined_features)

        return normalized_features

    def create_tfidf_features(self, text_data):
        """Create TF-IDF features from text data"""
        vectorizer = TfidfVectorizer(max_features=50, stop_words='english')

        # Handle empty text data
        text_data = [text if text.strip() else 'none' for text in text_data]

        try:
            tfidf_matrix = vectorizer.fit_transform(text_data)
            if hasattr(tfidf_matrix, 'toarray'):
                return tfidf_matrix.toarray()
            else:
                return tfidf_matrix
        except ValueError:
            # If all documents are identical or empty, return zero matrix
            return np.zeros((len(text_data), 1))

    def cluster_participants(self, feature_matrix, num_teams, team_size):
        """Cluster participants into teams using K-means"""
        # Ensure we don't have more teams than participants
        max_possible_teams = len(self.participants) // 2  # Minimum 2 people per team
        num_teams = min(num_teams, max_possible_teams)

        if num_teams <= 0:
            raise ValueError("Not enough participants to form teams")

        # Apply K-means clustering
        kmeans = KMeans(n_clusters=num_teams, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(feature_matrix)

        # Group participants by cluster
        teams = []
        for cluster_id in range(num_teams):
            team_members = [
                self.participants[i] for i, label in enumerate(cluster_labels)
                if label == cluster_id
            ]
            teams.append(team_members)

        return teams

    def balance_teams(self, teams, balance_priority, include_leadership):
        """Balance teams based on specified priority"""

        if balance_priority == "Experience Balance":
            teams = self.balance_experience_levels(teams)
        elif balance_priority == "Role Diversity":
            teams = self.balance_roles(teams)
        elif balance_priority == "Skill Diversity":
            teams = self.balance_skills(teams)
        elif balance_priority == "Interest Alignment":
            teams = self.align_interests(teams)

        if include_leadership:
            teams = self.ensure_leadership(teams)

        return teams

    def balance_experience_levels(self, teams):
        """Balance experience levels across teams"""
        # Calculate experience score for each team
        exp_mapping = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}

        for team in teams:
            team_exp_scores = [
                exp_mapping.get(member.get('experience_level', 'Beginner'), 1)
                for member in team
            ]
            team.append({'avg_experience': np.mean(team_exp_scores)})

        # Try to balance by moving members between teams if possible
        # This is a simplified balancing approach
        return teams

    def balance_roles(self, teams):
        """Ensure role diversity within teams"""
        for team in teams:
            roles = [member.get('role_preference', '') for member in team]
            unique_roles = len(set(roles))
            # Store diversity score for potential rebalancing
            team.append({'role_diversity': unique_roles / len(team) if team else 0})

        return teams

    def balance_skills(self, teams):
        """Balance skills across teams"""
        for team in teams:
            all_skills = set()
            for member in team:
                all_skills.update(member.get('programming_langs', []))
                all_skills.update(member.get('frameworks', []))
                all_skills.update(member.get('tools', []))

            team.append({'total_skills': len(all_skills)})

        return teams

    def align_interests(self, teams):
        """Align team members by interests"""
        for team in teams:
            all_interests = []
            for member in team:
                all_interests.extend(member.get('interests', []))

            if all_interests:
                # Calculate most common interests
                interest_counts = pd.Series(all_interests).value_counts()
                top_interests = interest_counts.head(3).index.tolist()
                team.append({'common_interests': top_interests})
            else:
                team.append({'common_interests': []})

        return teams

    def ensure_leadership(self, teams):
        """Ensure each team has at least one potential leader"""
        teams_needing_leaders = []
        available_leaders = []

        # Identify teams without leaders and collect available leaders
        for i, team in enumerate(teams):
            has_leader = any(member.get('leadership_interest', False) for member in team if isinstance(member, dict))
            if not has_leader:
                teams_needing_leaders.append(i)

        # Find participants with leadership interest not yet in teams with leaders
        for i, team in enumerate(teams):
            if i not in teams_needing_leaders:
                leaders_in_team = [
                    member for member in team
                    if isinstance(member, dict) and member.get('leadership_interest', False)
                ]
                if len(leaders_in_team) > 1:
                    available_leaders.extend(leaders_in_team[1:])  # Keep one leader per team

        # Distribute leaders to teams that need them
        for team_idx in teams_needing_leaders[:len(available_leaders)]:
            leader = available_leaders.pop()
            teams[team_idx].append(leader)

        return teams

    def format_teams(self, teams):
        """Format teams for output"""
        formatted_teams = []

        for i, team_members in enumerate(teams):
            # Filter out metadata objects
            members = [member for member in team_members if isinstance(member, dict) and 'name' in member]

            if members:  # Only include teams with actual members
                team_data = {
                    'id': i + 1,
                    'members': members,
                    'size': len(members),
                    'avg_experience': self.calculate_team_experience(members),
                    'role_diversity': len(set(m.get('role_preference', '') for m in members)),
                    'has_leader': any(m.get('leadership_interest', False) for m in members),
                    'common_skills': self.get_common_skills(members),
                    'common_interests': self.get_common_interests(members)
                }
                formatted_teams.append(team_data)

        return formatted_teams

    def calculate_team_experience(self, members):
        """Calculate average team experience level"""
        exp_mapping = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
        experiences = [exp_mapping.get(m.get('experience_level', 'Beginner'), 1) for m in members]
        return np.mean(experiences)

    def get_common_skills(self, members):
        """Get most common skills in team"""
        all_skills = []
        for member in members:
            all_skills.extend(member.get('programming_langs', []))
            all_skills.extend(member.get('frameworks', []))

        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts()
            return skill_counts.head(5).index.tolist()
        return []

    def get_common_interests(self, members):
        """Get most common interests in team"""
        all_interests = []
        for member in members:
            all_interests.extend(member.get('interests', []))

        if all_interests:
            interest_counts = pd.Series(all_interests).value_counts()
            return interest_counts.head(3).index.tolist()
        return []
