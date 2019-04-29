## Documentation
1. `/`:
    * `GET` -  a list of available base endpoints

2. `/restaurants/`:
    * `GET` - returns a list of restaurants
    * `POST` - creates a new restaurant, payload example 
        ```json
        {"name": "Restaurant Name"}
        ```
    
3. `/restaurants/{id}/`:
    * `GET` - returns a specific restaurant
    * `PUT/PATCH` - updates restaurant info if user is representative of a restaurant or admin, payload example 
        ```json
        {"name": "Updated Restaurant Name"}
        ```
    * `DELETE` - deletes restaurant if user is representative of a restaurant or admin
    
4. `/restaurants/{id}/today/`:
    * `GET` - returns today's menu of a restaurant
    
5. `/menus/`:
    * `GET` - returns a list of menus
    * `POST` - creates a new menu if user is representative of a restaurant or admin, example payload 
        ```json
        {
            "date": "2019-04-18", 
            "restaurant": "http://localhost:8000/restaurants/1/", 
            "description": "Pizza: 5$"
        }
        ```
    
6. `/menus/{id}/`:
    * `GET` - returns specific menu
    * `PUT/PATCH` - updates menu info if user is representative of a restaurant or admin, example payload 
        ```json
        {"description": "Pizza: 10$"}
        ```
    * `DELETE` - deletes restaurant if user is representative of a restaurant or admin

7. `/menus/{id}/vote/`:
    * `POST` - add/removes a vote for specific menu, only employees can vote
    
8. `/menus/today/`:
    * `GET` - returns today's menus 

9. `/menus/results/`:
    * `GET` - returns today's menus with vote count, if user is admin also a list of votes is returned
 
10. `/menuvote/`:
    * `GET` - returns a list of votes

11. `/menuvote/{id}/`:
    * `GET` - returns a specific vote

12. `/users/`:
    * `GET` - returns a list of users, if user is not admin only himself will be returned
    * `POST` - creates a new user account, available even to anonymous users, example payload 
        ```json
        {
            "username": "username", 
            "password": "password"
        }
        ```

13. `/users/{id}/`:
    * `GET` - returns a specific user, if user is not admin only his user info can be returned
    * `PUT/PATCH` - updates user info, if user is not admin only his user info can be updated, example payload 
        ```json
        {"username": "edited username"}
        ```
    * `DELETE` - deletes user info, if user is not admin only his user info can be deleted

14. `/profile/`:
    * `GET` - returns a list of profiles

15. `/profile/{id}/`:
    * `GET` - returns a specific user profile
    * `PUT/PATCH` - updates user profile, admin only, example payload 
        ```json
        {"employee": true}
        ```

16. `/log_entries/`:
    * `GET` - returns a list of log entries

17. `/log_entries/{id}/`:
    * `GET` - returns a specific of log entry
