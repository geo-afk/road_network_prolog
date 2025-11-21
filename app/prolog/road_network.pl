% road_network.pl - Store road network data and pathfinding algorithms

% ===== FACTS: Road Network Representation =====
% road(Source, Destination, Distance_Km, Type, Status)
:- dynamic road/5.
:- dynamic heuristic/3.

% Sample Jamaican rural roads
road(mandeville, may_pen, 25, paved, open).
road(may_pen, spanish_town, 30, paved, open).
road(spanish_town, kingston, 20, paved, open).
road(mandeville, christiana, 15, unpaved, open).
road(christiana, spaldings, 12, broken_cisterns, open).
road(spaldings, may_pen, 18, paved, open).
road(may_pen, old_harbour, 22, deep_potholes, open).
road(old_harbour, spanish_town, 15, paved, closed).

% Bidirectional roads (can travel both ways)
bidirectional_road(A, B, Dist, Type, Status) :-
    road(A, B, Dist, Type, Status).
bidirectional_road(A, B, Dist, Type, Status) :-
    road(B, A, Dist, Type, Status).

% ===== RULES: Road Filtering Based on Criteria =====

% Check if road is available based on user criteria
road_available(From, To, Dist, Type, Status, Criteria) :-
    bidirectional_road(From, To, Dist, Type, Status),
    check_criteria(Type, Status, Criteria).

% Criteria checking
check_criteria(Type, Status, Criteria) :-
    \+ (member(avoid_closed, Criteria), Status = closed),
    \+ (member(avoid_unpaved, Criteria), Type = unpaved),
    \+ (member(avoid_broken_cisterns, Criteria), Type = broken_cisterns),
    \+ (member(avoid_potholes, Criteria), Type = deep_potholes).

% ===== DIJKSTRA'S ALGORITHM =====
% Find shortest path using Dijkstra's algorithm
dijkstra_path(Start, Goal, Criteria, Path, TotalDistance) :-
    dijkstra([[0, Start, []]], Goal, Criteria, RevPath, TotalDistance),
    reverse(RevPath, Path).

dijkstra([[Dist, Goal, Path]|_], Goal, _, [Goal|Path], Dist) :- !.

dijkstra([[Dist, Current, Path]|Rest], Goal, Criteria, FinalPath, FinalDist) :-
    findall([NewDist, Next, [Current|Path]],
        (road_available(Current, Next, EdgeDist, _, _, Criteria),
         \+ member(Next, Path),
         NewDist is Dist + EdgeDist),
        Neighbors),
    append(Rest, Neighbors, NewQueue),
    sort(NewQueue, SortedQueue),
    dijkstra(SortedQueue, Goal, Criteria, FinalPath, FinalDist).

% ===== A* ALGORITHM =====
% Heuristic: straight-line distance estimate (define for your locations)
heuristic(mandeville, kingston, 50).
heuristic(may_pen, kingston, 35).
heuristic(spanish_town, kingston, 20).
heuristic(christiana, kingston, 60).
heuristic(spaldings, kingston, 45).
heuristic(old_harbour, kingston, 25).
% Add more heuristics or use 0 as default
heuristic(_, _, 0).

astar_path(Start, Goal, Criteria, Path, TotalDistance) :-
    heuristic(Start, Goal, H),
    astar([[H, 0, Start, []]], Goal, Criteria, RevPath, TotalDistance),
    reverse(RevPath, Path).

astar([[_, Dist, Goal, Path]|_], Goal, _, [Goal|Path], Dist) :- !.

astar([[_, Dist, Current, Path]|Rest], Goal, Criteria, FinalPath, FinalDist) :-
    findall([F, NewG, Next, [Current|Path]],
        (road_available(Current, Next, EdgeDist, _, _, Criteria),
         \+ member(Next, Path),
         NewG is Dist + EdgeDist,
         heuristic(Next, Goal, H),
         F is NewG + H),
        Neighbors),
    append(Rest, Neighbors, NewQueue),
    sort(NewQueue, SortedQueue),
    astar(SortedQueue, Goal, Criteria, FinalPath, FinalDist).

% ===== BFS ALGORITHM =====
bfs_path(Start, Goal, Criteria, Path) :-
    bfs([[Start]], Goal, Criteria, RevPath),
    reverse(RevPath, Path).

bfs([[Goal|Rest]|_], Goal, _, [Goal|Rest]) :- !.

bfs([[Current|Path]|Rest], Goal, Criteria, FinalPath) :-
    findall([Next, Current|Path],
        (road_available(Current, Next, _, _, _, Criteria),
         \+ member(Next, [Current|Path])),
        Neighbors),
    append(Rest, Neighbors, NewQueue),
    bfs(NewQueue, Goal, Criteria, FinalPath).

% ===== UTILITY PREDICATES =====

% Calculate total distance for a path
calculate_distance([], 0).
calculate_distance([_], 0).
calculate_distance([A, B|Rest], TotalDist) :-
    bidirectional_road(A, B, Dist, _, _),
    calculate_distance([B|Rest], RestDist),
    TotalDist is Dist + RestDist.

% Add new road (for admin updates)
add_road(From, To, Dist, Type, Status) :-
    assertz(road(From, To, Dist, Type, Status)).

% Update road status
update_road_status(From, To, NewStatus) :-
    retract(road(From, To, Dist, Type, _)),
    assertz(road(From, To, Dist, Type, NewStatus)).

% List all roads
list_all_roads(Roads) :-
    findall([From, To, Dist, Type, Status], 
            road(From, To, Dist, Type, Status), 
            Roads).