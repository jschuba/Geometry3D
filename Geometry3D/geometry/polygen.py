# -*- coding: utf-8 -*-
"""Polygen Module"""
from .body import GeoBody
from .point import Point
from ..utils.vector import Vector
from .line import Line
from .segment import Segment
from .plane import Plane
from ..utils.constant import *
import copy
import math

def get_triangle_area(pa,pb,pc):
    """
    **Input:**
    
    - pa: a Point
    
    - pb: a Point
    
    - pc: a Point

    **Output:**
    
    The area of the triangle composed by pa, pb and pc.

    Heron's formula is used
    """
    a = pa.distance(pb)
    b = pb.distance(pc)
    c = pc.distance(pa)
    p = (a + b + c) / 2
    return math.sqrt(p * (p - a) * (p - b) * (p - c))

class ConvexPolygen(GeoBody):
    """
    - ConvexPolygens(points)
    points: a tuple of points.

    The points needn't to be in order.

    The convexity should be guaranteed. This function **will not** check the convexity.
    If the Polygen is not convex, there might be errors.
    """
    class_level = 4 # the class level of ConvexPolygen
    @classmethod
    def Parallelogram(cls,base_point,v1,v2):
        """
        A special function for creating Parallelogram

        **Input:**

        - base_point: a Point

        - v1, v2: two Vectors

        **Output:**

        - A parallelogram which is a ConvexPolygen instance.
        """
        if isinstance(base_point,Point) and isinstance(v1,Vector) and isinstance(v2,Vector):
            if v1.length() == 0 or v2.length == 0:
                raise ValueError("The length for the two vector shouldn't be zero")
            elif v1.parallel(v2):
                raise ValueError("The two vectors shouldn't be parallel to each other")
            else:
                return cls((
                    base_point,
                    copy.deepcopy(base_point).move(v1),
                    copy.deepcopy(base_point).move(v2),
                    copy.deepcopy(base_point).move(v1).move(v2)
                ))
        else:
            raise TypeError("Parallelogram should be initialized with Point, Vector and Vector, but the given types are %s, %s and %s" %(type(base_point),type(v1),type(v2)))
    
    def __init__(self,pts,reverse = False, check_convex=False):
        # merge same points
        points = copy.deepcopy(pts)
        self.points = sorted(set(points),key=points.index)
        if len(points) < 3:
            raise ValueError('Cannot build a polygen with number of points smaller than 3')
        if reverse:
            self.plane = -Plane(self.points[0],self.points[1],self.points[2])
        else:
            self.plane = Plane(self.points[0],self.points[1],self.points[2])
    
        self.center_point = self._get_center_point()

        self._check_and_sort_points()

    def segments(self):
        """
        **Input:**
        
        - self

        **Output:**

        - iterator of segments
        """
        for i in range(len(self.points)):
            index_0 = i
            if i == len(self.points) - 1:
                index_1 = 0
            else:
                index_1 = i + 1
            yield Segment(self.points[index_0],self.points[index_1])
    
    def _get_center_point(self):
        """
        **Input:**
        
        - points: tuple of points

        **Output:**

        - The center point of given points
        """
        x,y,z =(0,0,0)
        num_points = len(self.points)
        for point in self.points:
            x += point.x
            y += point.y
            z += point.z
        return Point(float(x) / num_points,float(y) / num_points,float(z) / num_points)
    
    def area(self):
        """
        **Input:**
        
        - self

        **Output:**
        
        - The area of the convex polygen
        """
        area = 0
        for i in range(len(self.points)):
            index_0 = i
            if i == len(self.points) - 1:
                index_1 = 0
            else:
                index_1 = i + 1
            area += get_triangle_area(self.center_point,self.points[index_0],self.points[index_1])
        return area

    def _check_and_sort_points(self):
        """
        **Input:**
        
        -self

        **Output:**

        - True for check passed
        
        - False for check not passed

        This is only a **weak** check, passing the check doesn't guarantee it is a convex polygen
        """
        the_normal = (self.plane.n).normalized()
        v0 = Vector(self.center_point,self.points[0]).normalized()
        v1 = the_normal.cross(v0)
        angle_point_dict = dict() # dict[angle] = Point
        for point in self.points:
            if not point in self.plane:
                raise ValueError('Convex Check Fails Because {} Is Not On {}'.format(point,self.plane))
            pv = point.pv() - self.center_point.pv()
            y_coordinate = pv * v0
            z_coordinate = pv * v1
            # the range of vector_angle is [0,2*pi)
            vector_angle = math.atan2(z_coordinate,y_coordinate)
            if vector_angle < 0:
                vector_angle += 2 * math.pi
            angle_point_dict[vector_angle] = point
        point_list = [angle_point_dict[angle] for angle in sorted(angle_point_dict)]
        self.points = tuple(point_list)
        return True
    
    def __repr__(self):
        return "ConvexPolygen({})".format(self.points)

    def __contains__(self, other):
        """Checks if a point or segment lies in a ConvexPolygen"""
        if isinstance(other,Point):
            r1 = other in self.plane
            # requirement 1: the point is on the plane
            the_normal = self.plane.n.normalized()
            r2 = True
            # requirement 2: the point is inside the polygen
            for i in range(len(self.points)):
                # check if the point lies in the inside direction of every segment
                index_0 = i
                if i == len(self.points) - 1:
                    index_1 = 0
                else:
                    index_1 = i + 1
                # self.points[index_0] and self.points[index_1] is the i^th segment
                v0 = Vector(self.points[index_0],self.points[index_1])
                v1 = the_normal.cross(v0)
                vec = Vector(self.points[index_0],other)
                if vec * v1 < - get_eps():
                    r2 = False
                    break
            return r1 and r2
        
        elif isinstance(other,Segment):
            return (other.start_point in self) and (other.end_point in self)
        else:
            return NotImplementedError("")
    
    def in_(self,other):
        """
        **Input:**
        
        - self: ConvexPolygen
        
        - other: Plane

        **Output:**

        - whether self in other
        """
        if isinstance(other,Plane):
            return self.plane == other
        else:
            raise NotImplementedError("")

    def __eq__(self,other):
        if isinstance(other,ConvexPolygen):
            return (hash(self) == hash(other))
        else:
            return False
    
    
    def _get_point_hash_sum(self):
        """return the sum of hash of all points"""
        hash_sum = 0
        for point in self.points:
            hash_sum += hash(point)
        return hash_sum

    # the hash function is not accurate
    # in some extreme case, this function may fail
    # which means it's vulnerable to attacks.
    def __hash__(self):
        """return the has of the convexpolygen"""
        return hash(("ConvexPolygen",
        round(self._get_point_hash_sum(),SIG_FIGURES),
        hash(self.plane) + hash(-self.plane),
        hash(self.plane) * hash(-self.plane)
        ))


    def eq_with_normal(self,other):
        """return whether self equals with other considering the normal"""
        if isinstance(other,ConvexPolygen):
            return (self.hash_with_normal() == other.hash_with_normal())
        else:
            return False

    def hash_with_normal(self):
        """return the hash value considering the normal"""
        return hash(("ConvexPolygen",
            round(self._get_point_hash_sum(),SIG_FIGURES-5),
            hash(self.plane)
            ))

    def __neg__(self):
        """return the negative ConvexPolygen by reverting the normal"""
        return ConvexPolygen(self.points,reverse=True)

    def length(self):
        """return the total length of ConvexPolygen""" 
        length = 0
        for segment in self.segments():
            length += segment.length()
        return length

    def move(self,v):
        """Return the ConvexPolygen that you get when you move self by vector v, self is also moved"""
        if isinstance(v,Vector):
            point_list = []
            for point in self.points:
                point_list.append(point.move(v))
            self.points = tuple(point_list)
            self.plane = Plane(self.points[0],self.points[1],self.points[2])
            self.center_point = self._get_center_point()
            return ConvexPolygen(self.points)
        else:
            raise NotImplementedError("The second parameter for move function must be Vector")

Parallelogram = ConvexPolygen.Parallelogram

__all__ = ("ConvexPolygen","Parallelogram")