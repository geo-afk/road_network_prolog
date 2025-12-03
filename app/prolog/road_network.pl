% ===== FACTS: Comprehensive Jamaican Road Network =====
% road(Source, Destination, Distance_Km, Type, Status)
:- dynamic road/5.
:- dynamic heuristic/3.

% ===== CENTRAL JAMAICA - Major Routes =====
% Spanish Town connections (major hub)
road(spanish_town, kingston, 21, paved, open).
road(spanish_town, may_pen, 42, paved, open).
road(spanish_town, old_harbour, 15, paved, open).
road(spanish_town, linstead, 18, paved, open).
road(spanish_town, portmore, 12, paved, open).
road(spanish_town, bog_walk, 14, unpaved, open).

% May Pen connections (agricultural hub)
road(may_pen, mandeville, 39, paved, open).
road(may_pen, spanish_town, 42, paved, open).
road(may_pen, spaldings, 18, paved, open).
road(may_pen, chapelton, 16, unpaved, open).
road(may_pen, frankfield, 12, paved, open).
road(may_pen, lionel_town, 25, deep_potholes, open).
road(may_pen, hayes, 20, paved, open).

% Mandeville connections (Manchester Highlands)
road(mandeville, may_pen, 39, paved, open).
road(mandeville, christiana, 15, unpaved, open).
road(mandeville, santa_cruz, 32, paved, open).
road(mandeville, spaldings, 22, paved, open).
road(mandeville, newport, 8, paved, open).
road(mandeville, williamsfield, 10, unpaved, open).

% ===== CLARENDON PARISH =====
road(spaldings, may_pen, 18, paved, open).
road(spaldings, christiana, 12, broken_cisterns, open).
road(spaldings, mandeville, 22, paved, open).
road(chapelton, frankfield, 8, paved, open).
road(frankfield, may_pen, 12, paved, open).
road(lionel_town, hayes, 14, unpaved, open).
road(hayes, may_pen, 20, paved, open).
road(lionel_town, rocky_point, 18, unpaved, closed).

% ===== MANCHESTER PARISH =====
road(christiana, mandeville, 15, unpaved, open).
road(christiana, spaldings, 12, broken_cisterns, open).
road(newport, mandeville, 8, paved, open).
road(williamsfield, mandeville, 10, unpaved, open).
road(porus, mandeville, 16, deep_potholes, open).

% ===== ST. CATHERINE PARISH =====
road(old_harbour, spanish_town, 15, paved, open).
road(old_harbour, may_pen, 22, deep_potholes, open).
road(old_harbour, old_harbour_bay, 5, paved, open).
road(portmore, kingston, 14, paved, open).
road(portmore, spanish_town, 12, paved, open).
road(linstead, spanish_town, 18, paved, open).
road(linstead, bog_walk, 10, paved, open).
road(bog_walk, spanish_town, 14, unpaved, open).
road(ewarton, linstead, 12, paved, open).
road(ewarton, bog_walk, 8, paved, open).

% ===== KINGSTON & ST. ANDREW =====
road(kingston, spanish_town, 21, paved, open).
road(kingston, portmore, 14, paved, open).
road(kingston, half_way_tree, 6, paved, open).
road(kingston, papine, 8, paved, open).
road(half_way_tree, constant_spring, 4, paved, open).
road(half_way_tree, papine, 5, paved, open).
road(papine, gordon_town, 7, unpaved, open).
road(constant_spring, stony_hill, 6, paved, open).

% ===== SOUTH COAST ROUTE =====
road(mandeville, santa_cruz, 32, paved, open).
road(santa_cruz, black_river, 24, paved, open).
road(black_river, treasure_beach, 16, unpaved, open).
road(black_river, ys_falls, 12, unpaved, open).
road(black_river, middle_quarters, 8, paved, open).
road(black_river, lacovia, 10, paved, open).
road(middle_quarters, santa_cruz, 18, paved, open).
road(santa_cruz, malvern, 14, unpaved, open).
road(lacovia, black_river, 10, paved, open).

% St. Elizabeth Parish
road(santa_cruz, junction, 12, paved, open).
road(black_river, savanna_la_mar, 63, paved, open).
road(treasure_beach, alligator_pond, 22, unpaved, open).

% ===== WESTMORELAND PARISH =====
road(savanna_la_mar, negril, 26, paved, open).
road(savanna_la_mar, black_river, 63, paved, open).
road(negril, little_london, 18, paved, open).
road(little_london, savanna_la_mar, 15, paved, open).

% ===== NORTH COAST - Tourist Corridor =====
road(montego_bay, falmouth, 33, paved, open).
road(falmouth, discovery_bay, 32, paved, open).
road(discovery_bay, runaway_bay, 9, paved, open).
road(runaway_bay, st_anns_bay, 17, paved, open).
road(st_anns_bay, ocho_rios, 11, paved, open).
road(ocho_rios, port_maria, 28, paved, open).
road(port_maria, port_antonio, 42, paved, open).

% St. James Parish
road(montego_bay, lucea, 45, paved, open).
road(montego_bay, catadupa, 12, unpaved, open).
road(catadupa, maroon_town, 24, unpaved, closed).

% St. Ann Parish
road(ocho_rios, browns_town, 22, paved, open).
road(browns_town, alexandria, 14, unpaved, open).
road(st_anns_bay, claremont, 16, paved, open).
road(claremont, alexandria, 10, unpaved, open).
road(moneague, ocho_rios, 28, paved, open).

% ===== CROSS-ISLAND ROUTES =====
% Ocho Rios to Spanish Town
road(ocho_rios, moneague, 28, paved, open).
road(moneague, linstead, 19, paved, open).
road(linstead, spanish_town, 18, paved, open).

% Montego Bay to Mandeville
road(montego_bay, catadupa, 12, unpaved, open).
road(catadupa, santa_cruz, 45, unpaved, open).
road(santa_cruz, mandeville, 32, paved, open).

% ===== PORTLAND PARISH =====
road(port_antonio, buff_bay, 25, paved, open).
road(buff_bay, annotto_bay, 18, paved, open).
road(annotto_bay, port_maria, 22, paved, open).
road(port_antonio, fellowship, 15, unpaved, open).

% ===== ST. MARY PARISH =====
road(port_maria, ocho_rios, 28, paved, open).
road(port_maria, annotto_bay, 22, paved, open).
road(annotto_bay, buff_bay, 18, paved, open).

% ===== ST. THOMAS PARISH =====
road(kingston, morant_bay, 35, paved, open).
road(morant_bay, yallahs, 15, unpaved, open).
road(yallahs, bath, 20, unpaved, open).
road(morant_bay, golden_grove, 12, paved, open).

% ===== TRELAWNY PARISH =====
road(falmouth, duncans, 14, paved, open).
road(falmouth, wakefield, 18, unpaved, open).
road(duncans, rio_bueno, 10, paved, open).
road(wakefield, clarks_town, 12, unpaved, open).

% ===== HANOVER PARISH =====
road(lucea, green_island, 16, paved, open).
road(lucea, sandy_bay, 12, paved, open).
road(green_island, negril, 22, paved, open).

% ===== ADDITIONAL RURAL CONNECTIONS =====
% Remote and challenging roads
road(spaldings, porus, 16, deep_potholes, open).
road(christiana, newmarket, 10, broken_cisterns, open).
road(rocky_point, milk_river, 8, unpaved, closed).
road(alligator_pond, lionel_town, 28, deep_potholes, open).
road(stony_hill, castleton, 18, unpaved, open).
road(castleton, annotto_bay, 22, broken_cisterns, open).
road(maroon_town, accompong, 32, unpaved, closed).

% Secondary connections
road(frankfield, chapelton, 8, paved, open).
road(hayes, frankfield, 14, paved, open).
road(newport, porus, 12, unpaved, open).
road(williamsfield, christiana, 14, unpaved, open).
road(old_harbour_bay, rocky_point, 20, unpaved, open).

% ===== BIDIRECTIONAL ROAD PREDICATE =====
bidirectional_road(A, B, Dist, Type, Status) :-
    road(A, B, Dist, Type, Status).
bidirectional_road(A, B, Dist, Type, Status) :-
    road(B, A, Dist, Type, Status).

% ===== RULES: Road Filtering Based on Criteria =====
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
% Comprehensive heuristics based on approximate straight-line distances to Kingston
heuristic(kingston, kingston, 0).
heuristic(spanish_town, kingston, 18).
heuristic(portmore, kingston, 12).
heuristic(may_pen, kingston, 55).
heuristic(mandeville, kingston, 85).
heuristic(old_harbour, kingston, 30).
heuristic(linstead, kingston, 35).
heuristic(bog_walk, kingston, 32).
heuristic(half_way_tree, kingston, 5).
heuristic(papine, kingston, 7).
heuristic(constant_spring, kingston, 8).
heuristic(stony_hill, kingston, 12).

% South Coast
heuristic(black_river, kingston, 120).
heuristic(santa_cruz, kingston, 95).
heuristic(savanna_la_mar, kingston, 165).
heuristic(negril, kingston, 185).
heuristic(treasure_beach, kingston, 130).

% North Coast
heuristic(montego_bay, kingston, 170).
heuristic(ocho_rios, kingston, 90).
heuristic(port_antonio, kingston, 105).
heuristic(falmouth, kingston, 145).
heuristic(st_anns_bay, kingston, 95).
heuristic(port_maria, kingston, 78).

% Rural areas
heuristic(christiana, kingston, 75).
heuristic(spaldings, kingston, 65).
heuristic(porus, kingston, 70).
heuristic(morant_bay, kingston, 33).
heuristic(yallahs, kingston, 45).

% Default heuristic for unlisted locations
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

% Get all unique locations in the network
get_all_locations(Locations) :-
    findall(Loc, (road(Loc, _, _, _, _); road(_, Loc, _, _, _)), AllLocs),
    sort(AllLocs, Locations).

% Get roads by type
get_roads_by_type(Type, Roads) :-
    findall([From, To, Dist, Status], 
            road(From, To, Dist, Type, Status), 
            Roads).

% Get roads by status
get_roads_by_status(Status, Roads) :-
    findall([From, To, Dist, Type], 
            road(From, To, Dist, Type, Status), 
            Roads).

% Find all direct connections from a location
get_connections(Location, Connections) :-
    findall([To, Dist, Type, Status],
            bidirectional_road(Location, To, Dist, Type, Status),
            Connections).

% Check if path exists between two locations
path_exists(Start, Goal, Criteria) :-
    bfs_path(Start, Goal, Criteria, _).

% Add new road (for admin updates)
add_road(From, To, Dist, Type, Status) :-
    assertz(road(From, To, Dist, Type, Status)).

% Update road status
update_road_status(From, To, NewStatus) :-
    retract(road(From, To, Dist, Type, _)),
    assertz(road(From, To, Dist, Type, NewStatus)).

% Update road type
update_road_type(From, To, NewType) :-
    retract(road(From, To, Dist, _, Status)),
    assertz(road(From, To, Dist, NewType, Status)).

% Delete a road
delete_road(From, To) :-
    retract(road(From, To, _, _, _)).

% List all roads
list_all_roads(Roads) :-
    findall([From, To, Dist, Type, Status], 
            road(From, To, Dist, Type, Status), 
            Roads).

% Count roads by criteria
count_roads_by_type(Type, Count) :-
    findall(1, road(_, _, _, Type, _), List),
    length(List, Count).

count_roads_by_status(Status, Count) :-
    findall(1, road(_, _, _, _, Status), List),
    length(List, Count).

% Get network statistics
network_statistics(Stats) :-
    findall(1, road(_, _, _, _, _), AllRoads),
    length(AllRoads, TotalRoads),
    count_roads_by_type(paved, Paved),
    count_roads_by_type(unpaved, Unpaved),
    count_roads_by_type(broken_cisterns, BrokenCisterns),
    count_roads_by_type(deep_potholes, DeepPotholes),
    count_roads_by_status(open, Open),
    count_roads_by_status(closed, Closed),
    get_all_locations(Locs),
    length(Locs, TotalLocations),
    Stats = [
        total_roads(TotalRoads),
        total_locations(TotalLocations),
        paved(Paved),
        unpaved(Unpaved),
        broken_cisterns(BrokenCisterns),
        deep_potholes(DeepPotholes),
        open(Open),
        closed(Closed)
    ].