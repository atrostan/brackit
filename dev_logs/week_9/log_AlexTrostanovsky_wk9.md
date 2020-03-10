# Duties
Progression Handling; Only authenticated TO should be able (once match is done)

# Achievements
1) Implemented authentication to ensure `report-match` endpoint is only accessed using the tournament organizer
2) To enable `Guest` Users to join `Brackit` Tournaments, implemented the following:  
    a) Added a `Lobby` Model that will act as a temporary container for Tournament Organizers to store potential entrants  
    b) For each user checked in to a lobby, the TO inputs
    the following tuple `(User Name, User Role, User Seed)`  
    c) This ensures that users with `Guest` roles are not allowed to register with existing usernames  
    d) Once the TO adds all entrants, a tournament is created,
    and the lobby is purged

