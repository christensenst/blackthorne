"""
Social Network Example using Neo4j

This module demonstrates Neo4j's strengths in handling complex relationship queries
that would be difficult or inefficient with traditional relational databases.

Key benefits showcased:
1. Friend-of-friend recommendations
2. Shortest path between users
3. Community detection through shared interests
4. Multi-hop relationship traversal
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase, Driver


class SocialNetwork:
    """
    A social network implementation using Neo4j graph database.

    This example demonstrates real-world scenarios where Neo4j excels:
    - Finding friends of friends (2nd degree connections)
    - Discovering shortest paths between users
    - Recommending connections based on mutual friends
    - Finding communities through shared interests
    """

    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize connection to Neo4j database.
        """
        self.driver: Driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close the database connection."""
        self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_user(self, user_id: str, name: str, age: int, location: str) -> None:
        """
        Create a new user in the social network.
        """
        with self.driver.session() as session:
            session.run(
                """
                CREATE (u:User {
                    id: $user_id,
                    name: $name,
                    age: $age,
                    location: $location,
                    created_at: datetime()
                })
                """,
                user_id=user_id,
                name=name,
                age=age,
                location=location
            )

    def add_friendship(self, user1_id: str, user2_id: str, since: Optional[str] = None) -> None:
        """
        Create a bidirectional friendship relationship between two users.
        """
        if since is None:
            since = datetime.now().isoformat()
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u1:User {id: $user1_id})
                MATCH (u2:User {id: $user2_id})
                CREATE (u1)-[:FRIENDS_WITH {since: $since}]->(u2)
                CREATE (u2)-[:FRIENDS_WITH {since: $since}]->(u1)
                """,
                user1_id=user1_id,
                user2_id=user2_id,
                since=since
            )

    def add_interest(self, user_id: str, interest: str) -> None:
        """
        Add an interest to a user's profile.
        """
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $user_id})
                MERGE (i:Interest {name: $interest})
                CREATE (u)-[:INTERESTED_IN]->(i)
                """,
                user_id=user_id,
                interest=interest
            )

    def find_friends_of_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find second-degree connections (friends of friends) who aren't already friends.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (user:User {id: $user_id})-[:FRIENDS_WITH]->(friend)
                      -[:FRIENDS_WITH]->(fof:User)
                WHERE user <> fof
                  AND NOT (user)-[:FRIENDS_WITH]->(fof)
                RETURN fof.id AS user_id,
                       fof.name AS name,
                       fof.location AS location,
                       COUNT(DISTINCT friend) AS mutual_friends
                ORDER BY mutual_friends DESC
                LIMIT 10
                """,
                user_id=user_id
            )
            return [dict(record) for record in result]

    def find_shortest_connection_path(
        self,
        user1_id: str,
        user2_id: str
    ) -> Optional[List[str]]:
        """
        Find the shortest friendship path between two users.
        This demonstrates Neo4j's efficient path-finding algorithms.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = shortestPath(
                    (u1:User {id: $user1_id})-[:FRIENDS_WITH*]-(u2:User {id: $user2_id})
                )
                RETURN [node in nodes(path) | node.name] AS path
                """,
                user1_id=user1_id,
                user2_id=user2_id
            )
            record = result.single()
            return record["path"] if record else None

    def recommend_friends_by_interests(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Recommend potential friends based on shared interests.
        This showcases Neo4j's ability to traverse multiple relationship types and aggregate data efficiently.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (user:User {id: $user_id})-[:INTERESTED_IN]->(interest)
                      <-[:INTERESTED_IN]-(other:User)
                WHERE user <> other
                  AND NOT (user)-[:FRIENDS_WITH]->(other)
                WITH other, COUNT(DISTINCT interest) AS shared_interests,
                     COLLECT(DISTINCT interest.name) AS common_interests
                RETURN other.id AS user_id,
                       other.name AS name,
                       other.location AS location,
                       shared_interests,
                       common_interests
                ORDER BY shared_interests DESC
                LIMIT 10
                """,
                user_id=user_id
            )
            return [dict(record) for record in result]

    def find_communities(self, min_connections: int = 3) -> List[Dict[str, Any]]:
        """
        Find tightly-knit communities based on shared interests.
        This demonstrates Neo4j's pattern matching capabilities for discovering graph structures.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (i:Interest)<-[:INTERESTED_IN]-(u:User)
                WITH i, COLLECT(u.name) AS members, COUNT(u) AS size
                WHERE size >= $min_connections
                RETURN i.name AS interest,
                       size,
                       members
                ORDER BY size DESC
                """,
                min_connections=min_connections
            )
            return [dict(record) for record in result]

    def get_network_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive network statistics for a user.
        This shows how Neo4j can efficiently compute multiple graph metrics in a single query.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (user:User {id: $user_id})
                OPTIONAL MATCH (user)-[:FRIENDS_WITH]->(friend)
                OPTIONAL MATCH (user)-[:INTERESTED_IN]->(interest)
                OPTIONAL MATCH (user)-[:FRIENDS_WITH]->()-[:FRIENDS_WITH]->(fof)
                WHERE NOT (user)-[:FRIENDS_WITH]->(fof) AND user <> fof
                RETURN user.name AS name,
                       COUNT(DISTINCT friend) AS friend_count,
                       COUNT(DISTINCT interest) AS interest_count,
                       COUNT(DISTINCT fof) AS potential_connections
                """,
                user_id=user_id
            )
            record = result.single()
            return dict(record) if record else {}

    def clear_database(self) -> None:
        """
        Clear all data from the database (useful for testing).
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")


def create_demo_network() -> SocialNetwork:
    """
    Create a demo social network with sample data.
    """
    network = SocialNetwork("bolt://localhost:7687", "neo4j", "white_rabbit")

    # Clear existing data
    network.clear_database()

    # Create users
    users = [
        ("alice", "Alice Johnson", 28, "New York"),
        ("bob", "Bob Smith", 32, "San Francisco"),
        ("carol", "Carol White", 25, "New York"),
        ("david", "David Brown", 30, "Boston"),
        ("eve", "Eve Davis", 27, "San Francisco"),
        ("frank", "Frank Miller", 35, "Chicago"),
        ("grace", "Grace Wilson", 29, "New York"),
        ("henry", "Henry Moore", 31, "Boston"),
    ]

    for user_id, name, age, location in users:
        network.create_user(user_id, name, age, location)

    # Create friendships
    friendships = [
        ("alice", "bob"),
        ("alice", "carol"),
        ("alice", "grace"),
        ("bob", "david"),
        ("bob", "eve"),
        ("carol", "grace"),
        ("david", "henry"),
        ("eve", "frank"),
        ("frank", "henry"),
    ]

    for user1, user2 in friendships:
        network.add_friendship(user1, user2)

    # Add interests
    interests = {
        "alice": ["photography", "hiking", "cooking"],
        "bob": ["hiking", "technology", "gaming"],
        "carol": ["cooking", "photography", "travel"],
        "david": ["technology", "gaming", "music"],
        "eve": ["travel", "photography", "yoga"],
        "frank": ["music", "cooking", "gaming"],
        "grace": ["yoga", "cooking", "travel"],
        "henry": ["music", "technology", "hiking"],
    }

    for user_id, user_interests in interests.items():
        for interest in user_interests:
            network.add_interest(user_id, interest)

    return network


def run_demo():
    """
    Run a complete demonstration of Neo4j capabilities.

    This function shows the kind of queries that are painful in SQL
    but elegant and efficient in Neo4j.
    """
    print("=" * 60)
    print("Neo4j Social Network Demo")
    print("=" * 60)

    network = create_demo_network()

    try:
        # Demo 1: Friend recommendations
        print("\n1. FRIEND RECOMMENDATIONS (Friends of Friends)")
        print("-" * 60)
        print("Finding recommendations for Alice...")
        recommendations = network.find_friends_of_friends("alice")
        for rec in recommendations:
            print(f"  • {rec['name']} ({rec['location']}) - "
                  f"{rec['mutual_friends']} mutual friends")

        # Demo 2: Shortest path
        print("\n2. SHORTEST CONNECTION PATH")
        print("-" * 60)
        print("How is Alice connected to Henry?")
        path = network.find_shortest_connection_path("alice", "henry")
        if path:
            print(f"  Path: {' → '.join(path)}")
            print(f"  Degrees of separation: {len(path) - 1}")

        # Demo 3: Interest-based recommendations
        print("\n3. RECOMMENDATIONS BY SHARED INTERESTS")
        print("-" * 60)
        print("People Alice might like based on interests...")
        interest_recs = network.recommend_friends_by_interests("alice")
        for rec in interest_recs:
            print(f"  • {rec['name']} - {rec['shared_interests']} shared interests")
            print(f"    Common: {', '.join(rec['common_interests'])}")

        # Demo 4: Community detection
        print("\n4. INTEREST COMMUNITIES")
        print("-" * 60)
        print("Popular interests forming communities...")
        communities = network.find_communities(min_connections=3)
        for comm in communities:
            print(f"  • {comm['interest']}: {comm['size']} members")
            print(f"    {', '.join(comm['members'])}")

        # Demo 5: Network statistics
        print("\n5. NETWORK STATISTICS")
        print("-" * 60)
        for user_id in ["alice", "bob", "frank"]:
            stats = network.get_network_statistics(user_id)
            print(f"  {stats['name']}:")
            print(f"    Friends: {stats['friend_count']}")
            print(f"    Interests: {stats['interest_count']}")
            print(f"    Potential connections: {stats['potential_connections']}")

        print("\n" + "=" * 60)
        print("Demo complete!")
        print("=" * 60)

    finally:
        network.close()


if __name__ == "__main__":
    run_demo()
