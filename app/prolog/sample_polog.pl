% Real Jamaican locations in Portland Parish
road(moore_town, fellowship, 8, unpaved, open, 'Portland rural route').
road(fellowship, comfort_castle, 12, paved, open, 'B1 Highway').
road(comfort_castle, buff_bay, 6, paved, open, 'A4 Coastal route').

% Road conditions
road_condition(fellowship, moore_town, deep_potholes).
road_condition(comfort_castle, fellowship, broken_cisterns).

% Add Jamaican-specific conditions
weather_impact(rainy_season, unpaved, 2.5).  % 2.5x slower
weather_impact(hurricane_season, coastal, closed).


% Multi-criteria optimization
find_best_route(Start, End, Preferences, Route) :-
    % Weight different factors
    Preferences = [avoid_unpaved:0.8, minimize_distance:0.6, avoid_closed:1.0],
    % Calculate weighted score
    optimal_path(Start, End, Preferences, Route).

% Emergency response
emergency_route(Start, End, emergency_type, Route) :-
    emergency_type = ambulance,
    % Ignore some constraints for emergencies
    allow_controlled_closed_roads(Route).



% Calculate fuel costs based on road type
fuel_consumption(paved, 12).      % km per liter
fuel_consumption(unpaved, 8).     % worse on unpaved
fuel_consumption(deep_potholes, 6).

estimate_trip_cost(Route, TotalCost) :-
    calculate_fuel_needed(Route, Liters),
    fuel_price_jamaica(PricePerLiter),
    TotalCost is Liters * PricePerLiter.


dijkstra(Start, End, Path, TotalDistance) :-
    dijkstra_impl([[0, Start, []]], End, Path, TotalDistance).
