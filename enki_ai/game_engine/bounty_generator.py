import sqlite3
import uuid

class BountyGenerator:
    def __init__(self, db_path='enki_knowledge.db'):
        self.conn = sqlite3.connect(db_path)
        self.init_bounty_table()

    def init_bounty_table(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS community_bounties 
                     (id TEXT PRIMARY KEY, task_name TEXT, sector TEXT, 
                      reward_credits REAL, status TEXT)''')
        self.conn.commit()

    def generate_from_thesis(self, thesis_remedy, sector):
        """
        Extracts a physical task from the Thesis Remedy.
        Example: 'Build a PET-Graphene filter for the Mersey' 
        becomes a community quest.
        """
        bounty_id = str(uuid.uuid4())[:8]
        # Base reward on the 29th Node Frequency (Titan-Spec)
        reward = 1618.0 
        
        print(f"\n[BOUNTY] 💰 NEW QUEST IDENTIFIED: {thesis_remedy}")
        
        c = self.conn.cursor()
        c.execute("INSERT INTO community_bounties (id, task_name, sector, reward_credits, status) VALUES (?,?,?,?,?)",
                  (bounty_id, thesis_remedy, sector, reward, 'OPEN'))
        self.conn.commit()
        
        print(f"[HUD] ✅ BOUNTY POSTED: ID-{bounty_id} | REWARD: {reward} Credits.")
        print(f"[HUD] 🌐 BROADCASTING TO M32 MESH...")
        return bounty_id

if __name__ == "__main__":
    generator = BountyGenerator()
    # Simulating a remedy extracted from your Thesis Sector 1
    generator.generate_from_thesis("Install Graphene-PET Water Filter at Mersey Node 01", "Hydrology")
