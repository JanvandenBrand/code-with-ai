from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import numpy as np
import os
import pandas as pd
import json


# Creates the database for the social network

def create_database():
    Base = declarative_base()

    friendships = Table('friendships', Base.metadata,
                        Column('person_id', Integer, ForeignKey('people.id'), primary_key=True),
                        Column('friend_id', Integer, ForeignKey('people.id'), primary_key=True))

    club_members = Table('club_members', Base.metadata,
                         Column('person_id', Integer, ForeignKey('people.id'), primary_key=True),
                         Column('club_id', Integer, ForeignKey('clubs.id'), primary_key=True))

    class Person(Base):
        __tablename__ = 'people'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)
        gender = Column(String)
        location = Column(String)
        friends = relationship("Person",
                               secondary=friendships,
                               primaryjoin=id == friendships.c.person_id,
                               secondaryjoin=id == friendships.c.friend_id)
        clubs = relationship("Club", secondary=club_members, back_populates="members")

    class Club(Base):
        __tablename__ = 'clubs'
        id = Column(Integer, primary_key=True)
        description = Column(String)
        members = relationship("Person", secondary=club_members, back_populates="clubs")

    if os.path.exists("social_network.db"):
        os.remove("social_network.db")
    engine = create_engine(f'sqlite:///{"social_network.db"}', echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session, Club, Person, friendships, club_members


# Function to load data from CSV into the database
def load_data_from_csv(session, Club, Person, friendships, club_members, csv_path="members.csv"):
    # Step 1: Clear existing data from all relevant tables
    session.query(Person).delete()
    session.query(Club).delete()
    session.query(friendships).delete()
    session.query(club_members).delete()

    session.commit()  # Commit the deletion of all existing records

    # Load the CSV data
    df = pd.read_csv("members.csv", converters = {'Friendships': eval, "Clubs": eval})
        
    # Create a dictionary to store Person objects by ID
    persons_dict = {}
    
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Create a new Person object
        person = Person(
            id=row['ID'],
            name=f"{row['Name']} {row['Surname']}",
            age=row['Age'],
            gender=row['Gender'],
            location=row['Location']
        )
        # Add the person to the session and the dictionary
        session.add(person)
        persons_dict[row['ID']] = person
    
    # Commit the session to save the persons
    session.commit()
    
    # Iterate through each row again to create friendships and clubs
    for index, row in df.iterrows():
        person = persons_dict[row['ID']]
        
        # Create friendships
        for friend_id in row['Friendships']:
            friend = persons_dict.get(friend_id)
            if friend:
                person.friends.append(friend)
        
        # Create clubs
        for club_name in row['Clubs']:
            club = session.query(Club).filter_by(description=club_name).first()
            if not club:
                club = Club(description=club_name)
                session.add(club)
            person.clubs.append(club)
    
    # Commit the session to save the relationships
    session.commit()


def get_club_members(session, club_description):
    """
    Returns a list of Person objects who are members of a club given the club's description.
    
    Parameters:
    - session: The SQLAlchemy session for database queries.
    - club_description (str): The description of the club for which members are to be retrieved.
    
    Returns:
    - List[Person]: A list of Person objects who are members of the specified club.
    """
    # Query the Club table to find the club with the given description
    club = session.query(Club).filter_by(description=club_description).first()
    
    # If the club is found, return its members
    if club:
        return club.members
    else:
        return []
    

def get_friends_of_person(session, person_name):
    """
    Returns a list of Person objects who are friends with the specified person.
    
    Parameters:
    - session: The SQLAlchemy session object used to query the database.
    - person_name (str): The name of the person for whom to retrieve friends.
    
    Returns:
    - List[Person]: A list of Person objects who are friends with the specified person.
    """
    # Query the Person table to find the person with the given name
    person = session.query(Person).filter_by(name=person_name).first()
    
    # If the person is found, return their friends
    if person:
        return person.friends
    else:
        return []
    
def get_persons_who_consider_them_friend(session, person_name):
    """
    Returns a list of Person objects who consider the specified person as their friend,
    in a scenario where friendships are unidirectional.
    
    Parameters:
    - person_name (str): The name of the person to find who is considered as a friend by others.
    
    Returns:
    - List[Person]: A list of Person objects who consider the specified person as their friend.
    """
    # Query the Person table to find the person with the given name
    person = session.query(Person).filter_by(name=person_name).first()
    
    # If the person is not found, return an empty list
    if not person:
        return []
    
    # Query the Person table to find all persons who have the specified person in their friends list
    persons_who_consider_them_friend = session.query(Person).filter(Person.friends.contains(person)).all()
    
    return persons_who_consider_them_friend

    