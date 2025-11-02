# Social Network Module - Neo4j Demo

A comprehensive example demonstrating Neo4j's strengths in handling complex relationship queries through a social network use case.

## Why Neo4j?

This example showcases scenarios where graph databases excel over traditional relational databases:

### 1. **Friend-of-Friend Queries**
In SQL, finding friends of friends requires complex self-joins:
```sql
-- SQL version: Complex and slow
SELECT DISTINCT u3.*
FROM users u1
JOIN friendships f1 ON u1.id = f1.user1_id
JOIN friendships f2 ON f1.user2_id = f2.user1_id
JOIN users u3 ON f2.user2_id = u3.id
WHERE u1.id = ? AND u3.id != ? AND NOT EXISTS (...)
```

In Neo4j, it's intuitive and fast:
```cypher
// Neo4j version: Simple and efficient
MATCH (user)-[:FRIENDS_WITH]->()-[:FRIENDS_WITH]->(fof)
WHERE NOT (user)-[:FRIENDS_WITH]->(fof)
RETURN fof
```

### 2. **Shortest Path Finding**
Neo4j has built-in path-finding algorithms that would be extremely difficult to implement efficiently in SQL.

### 3. **Multi-hop Relationship Traversal**
Graph databases traverse relationships in constant time, while SQL joins get exponentially slower with each "hop."

### 4. **Pattern Matching**
Finding complex patterns in relationships is natural in graph query languages but painful in SQL.

## Features Demonstrated

- **User Management**: Create users and friendships
- **Friend Recommendations**: Find friends-of-friends who aren't already connected
- **Path Finding**: Discover the shortest connection between any two users
- **Interest Matching**: Recommend connections based on shared interests
- **Community Detection**: Identify groups of users with common interests
- **Network Statistics**: Compute various graph metrics efficiently

## Prerequisites

1. **Neo4j Database**
   - Download from: https://neo4j.com/download/
   - Or use Docker:
     ```bash
     docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
     ```

2. **Python Dependencies**
   ```bash
   pip install neo4j
   ```

## Usage

### Running the Demo

```python
from blackthorne.social.network import run_demo

# This will create sample data and demonstrate all features
run_demo()
```

### Using the API

```python
from blackthorne.social import SocialNetwork

# Connect to Neo4j
with SocialNetwork("bolt://localhost:7687", "neo4j", "password") as network:
    # Create users
    network.create_user("user1", "John Doe", 30, "New York")
    network.create_user("user2", "Jane Smith", 28, "Boston")

    # Create friendship
    network.add_friendship("user1", "user2")

    # Add interests
    network.add_interest("user1", "photography")
    network.add_interest("user2", "photography")

    # Find recommendations
    recommendations = network.find_friends_of_friends("user1")

    # Find connection path
    path = network.find_shortest_connection_path("user1", "user2")

    # Get network statistics
    stats = network.get_network_statistics("user1")
```

## Example Output

```
============================================================
Neo4j Social Network Demo
============================================================

1. FRIEND RECOMMENDATIONS (Friends of Friends)
------------------------------------------------------------
Finding recommendations for Alice...
  • David Brown (Boston) - 1 mutual friends
  • Eve Davis (San Francisco) - 1 mutual friends

2. SHORTEST CONNECTION PATH
------------------------------------------------------------
How is Alice connected to Henry?
  Path: Alice Johnson → Bob Smith → David Brown → Henry Moore
  Degrees of separation: 3

3. RECOMMENDATIONS BY SHARED INTERESTS
------------------------------------------------------------
People Alice might like based on interests...
  • Eve Davis - 2 shared interests
    Common: photography, travel
  • Frank Miller - 1 shared interests
    Common: cooking

4. INTEREST COMMUNITIES
------------------------------------------------------------
Popular interests forming communities...
  • cooking: 4 members
    Alice Johnson, Carol White, Frank Miller, Grace Wilson
  • photography: 3 members
    Alice Johnson, Carol White, Eve Davis

5. NETWORK STATISTICS
------------------------------------------------------------
  Alice Johnson:
    Friends: 3
    Interests: 3
    Potential connections: 3
```

## Key Benefits Highlighted

1. **Performance**: Graph traversals are O(1) for each hop, regardless of database size
2. **Simplicity**: Queries mirror how we think about relationships
3. **Flexibility**: Easy to add new relationship types without schema changes
4. **Insights**: Natural fit for recommendation engines and social analytics

## When to Use Neo4j

✅ **Great for:**
- Social networks
- Recommendation engines
- Fraud detection
- Network analysis
- Knowledge graphs
- Access control systems

❌ **Not ideal for:**
- Simple CRUD operations
- Aggregations over large datasets
- Traditional reporting
- Time-series data

## Structure

```
blackthorne/social/
├── __init__.py          # Module exports
├── network.py           # Main SocialNetwork class and demo
└── README.md           # This file
```

## API Reference

### SocialNetwork Class

#### Connection Management
- `__init__(uri, username, password)`: Initialize database connection
- `close()`: Close connection
- Context manager support with `with` statement

#### User Management
- `create_user(user_id, name, age, location)`: Create a new user
- `add_friendship(user1_id, user2_id, since=None)`: Create bidirectional friendship
- `add_interest(user_id, interest)`: Add interest to user profile

#### Recommendations & Discovery
- `find_friends_of_friends(user_id)`: Get 2nd-degree connection recommendations
- `find_shortest_connection_path(user1_id, user2_id)`: Find shortest path between users
- `recommend_friends_by_interests(user_id)`: Recommend users with shared interests
- `find_communities(min_connections=3)`: Discover interest-based communities
- `get_network_statistics(user_id)`: Get comprehensive network metrics

#### Utilities
- `clear_database()`: Remove all data (use with caution!)

## Further Reading

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Graph Database Use Cases](https://neo4j.com/use-cases/)
- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
