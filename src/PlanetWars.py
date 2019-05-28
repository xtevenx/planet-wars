#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout


class Fleet:
    def __init__(self, owner, num_ships, source_planet, destination_planet,
                 total_trip_length, turns_remaining):
        self._owner = owner
        self._num_ships = num_ships
        self._source_planet = source_planet
        self._destination_planet = destination_planet
        self._total_trip_length = total_trip_length
        self._turns_remaining = turns_remaining

    def Owner(self):
        return self._owner

    def NumShips(self):
        return self._num_ships

    def SourcePlanet(self):
        return self._source_planet

    def DestinationPlanet(self):
        return self._destination_planet

    def TotalTripLength(self):
        return self._total_trip_length

    def TurnsRemaining(self):
        return self._turns_remaining


class Planet:
    def __init__(self, planet_id, owner, num_ships, growth_rate, x, y):
        self._planet_id = planet_id
        self._owner = owner
        self._num_ships = num_ships
        self._growth_rate = growth_rate
        self._x = x
        self._y = y

        self.actual_ships = num_ships
        self.defend_ships = num_ships

        self.dying = False

    def PlanetID(self):
        return self._planet_id

    def Owner(self, new_owner=None):
        if new_owner is None:
            return self._owner
        self._owner = new_owner

    def NumShips(self, new_num_ships=None):
        if new_num_ships is None:
            return self._num_ships
        self._num_ships = new_num_ships

    def GrowthRate(self):
        return self._growth_rate

    def X(self):
        return self._x

    def Y(self):
        return self._y

    def AddShips(self, amount):
        self._num_ships += amount

    def RemoveShips(self, amount):
        self._num_ships -= amount


class PlanetWars:
    def __init__(self):
        self._planets = []
        self._fleets = []

        self._planet_id_counter = 0
        self._temporary_fleets = {}

        self._issued_orders = {}
        self._distance_cache = {}

    def NumPlanets(self):
        return len(self._planets)

    def GetPlanet(self, planet_id):
        return self._planets[planet_id]

    def NumFleets(self):
        return len(self._fleets)

    def GetFleet(self, fleet_id):
        return self._fleets[fleet_id]

    def Planets(self):
        return self._planets

    def MyPlanets(self):
        return list(filter(lambda p: p.Owner() == 1, self._planets))

    def NeutralPlanets(self):
        return list(filter(lambda p: p.Owner() == 0, self._planets))

    def EnemyPlanets(self):
        return list(filter(lambda p: p.Owner() == 2, self._planets))

    def NotMyPlanets(self):
        return list(filter(lambda p: p.Owner() != 1, self._planets))

    def Fleets(self):
        return self._fleets

    def MyFleets(self):
        return list(filter(lambda f: f.Owner() == 1, self._fleets))

    def EnemyFleets(self):
        return list(filter(lambda f: f.Owner() == 2, self._fleets))

    def ToString(self):
        s = ''
        for p in self._planets:
            s += "P %f %f %d %d %d\n" % \
                 (p.X(), p.Y(), p.Owner(), p.NumShips(), p.GrowthRate())
        for f in self._fleets:
            s += "F %d %d %d %d %d %d\n" % \
                 (f.Owner(), f.NumShips(), f.SourcePlanet(), f.DestinationPlanet(),
                  f.TotalTripLength(), f.TurnsRemaining())
        return s

    def Distance(self, source_planet, destination_planet):
        try:
            return self._distance_cache[tuple(sorted((source_planet, destination_planet)))]
        except KeyError:
            source = self._planets[source_planet]
            destination = self._planets[destination_planet]
            dx = source.X() - destination.X()
            dy = source.Y() - destination.Y()
            distance = int(ceil(sqrt(dx * dx + dy * dy)))
            self._distance_cache[tuple(sorted((source_planet, destination_planet)))] = distance
            return distance

    def IssueOrder(self, source_planet, destination_planet, num_ships):
        if num_ships == 0 or source_planet == destination_planet:
            return

        key = (source_planet, destination_planet)

        # for planet in self.MyPlanets():
        #     if planet.PlanetID() in key:
        #         continue
        #     if self.Distance(source_planet, planet.PlanetID()) + \
        #             self.Distance(planet.PlanetID(), destination_planet) == \
        #             self.Distance(source_planet, destination_planet):
        #         key = (source_planet, planet.PlanetID())

        try:
            self._issued_orders[key] += num_ships
        except KeyError:
            self._issued_orders[key] = num_ships

    def IsAlive(self, player_id):
        for p in self._planets:
            if p.Owner() == player_id:
                return True
        for f in self._fleets:
            if f.Owner() == player_id:
                return True
        return False

    def ParseGameState(self, s):
        lines = s.split("\n")

        for line in lines:
            line = line.split("#")[0]  # remove comments
            tokens = line.split(" ")
            if len(tokens) == 1:
                continue
            if tokens[0] == "P":
                if len(tokens) != 6:
                    return False
                p = Planet(self._planet_id_counter,  # The ID of this planet
                           int(tokens[3]),  # Owner
                           int(tokens[4]),  # Num ships
                           int(tokens[5]),  # Growth rate
                           float(tokens[1]),  # X
                           float(tokens[2]))  # Y
                self._planet_id_counter += 1
                self._planets.append(p)
            elif tokens[0] == "F":
                if len(tokens) != 7 or int(tokens[2]) == 0:
                    return False
                key = (int(tokens[1]), int(tokens[4]), int(tokens[6]))
                try:
                    self._temporary_fleets[key][0] += int(tokens[2])
                except KeyError:
                    self._temporary_fleets[key] = [int(tokens[2]), int(tokens[3]), int(tokens[5])]
            else:
                return False
        return True

    def Initialise(self):
        for (owner, destination, turns_remaining), (num_ships, source, trip_length) in self._temporary_fleets.items():
            f = Fleet(int(owner),  # Owner
                      int(num_ships),  # Num ships
                      int(source),  # Source
                      int(destination),  # Destination
                      int(trip_length),  # Total trip length
                      int(turns_remaining))  # Turns remaining
            self._fleets.append(f)

    def FinishTurn(self):
        for (source_planet, destination_planet), num_ships in self._issued_orders.items():
            stdout.write("%d %d %d\n" % (source_planet, destination_planet, num_ships))

        stdout.write("go\n")
        stdout.flush()
