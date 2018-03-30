/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file suitpathfinder_ai.h
 * @author Brian Lach
 * @date 2017-03-03
 */

#ifndef SUITPATHFINDER_AI_H
#define SUITPATHFINDER_AI_H

#include <referenceCount.h>
#include <py_panda.h>
#include <lvector2.h>
#include <lmatrix.h>

class AStarVertex : public ReferenceCount
{
public:
        AStarVertex( const LVector2f &vert );

        void link( AStarVertex *nbr );
        void unlink( AStarVertex *nbr );
        void unlink_all();
        void reset_neighbors();

        void set_polygonal_neighbors( AStarVertex *prev, AStarVertex *next );
        void extrude_vertex( float distance );

        bool is_vertex_inside_angle( AStarVertex *other ) const;
        bool is_vertex_inside_opposite( AStarVertex *other ) const;

        bool is_vertex_polygonal_neighbor( AStarVertex *other ) const;

        vector<AStarVertex *> get_neighbors() const;

        float get_heuristic_to( AStarVertex *other ) const;
        float get_cost_to( AStarVertex *other ) const;

        float get_interior_angle() const;

        LVector2f get_pos() const;

private:
        LVector2f _pos;
        AStarVertex *_prev_poly_nbr;
        AStarVertex *_next_poly_nbr;
        float _interior_angle;
        LVector2f _extrude_vector;
        bool _do_extrusion;
        bool _has_interior_angle;

        vector<AStarVertex *> _neighbors;

        void add_neighbor( AStarVertex *nbr );
        void remove_neighbor( AStarVertex *nbr );
};

class AStarPath : public ReferenceCount
{
public:
        AStarPath( AStarPath *p, AStarVertex *v, double tc, double h );

        //bool operator <(const AStarPath &other) const;

        AStarPath *parent;
        AStarVertex *vertex;
        double heuristic;
        double total_cost;
};

class AStarSearch
{
public:

        struct SearchResult
        {
                bool success;
                vector<AStarVertex *> pathverts;
        };

        AStarSearch();
        SearchResult search( AStarVertex *fromvert, AStarVertex *tovert );

private:

        vector<AStarVertex *> get_vertices_to_path( AStarPath *path );
        void do_iteration();

        vector<PT( AStarPath )> _open_list;
        vector<AStarVertex *> _closed_list;
        map<AStarVertex *, PT( AStarPath )> _paths;

        AStarVertex *_to_vert;
};

class SuitPathFinderAI
{
PUBLISHED:
        //                       list 
        SuitPathFinderAI( PyObject *polygons = nullptr );

        //                       tuple           tuple
        PyObject *plan_path( PyObject *from, PyObject *to, PN_stdfloat close_enough = 0.0f );

        //      list
        void add_polygon( PyObject *points );
        void build_neighbors();

private:

        struct PPTLResult
        {
                bool success;
                LVector2f result;
        };

        struct MLMResult
        {
                bool success;
                LMatrix3f result;
        };

        typedef vector<double> BorderPoints;
        vector<BorderPoints> _borders;

        vector<PT( AStarVertex )> _vertices;

        MLMResult make_line_mat( float x1, float y1, float x2, float y2 );
        void consider_link( AStarVertex *v1, AStarVertex *v2, bool test_angles = true );
        bool test_line_intersections( vector<float> points, vector<BorderPoints> bords );
        PPTLResult project_point_to_line( LVector2f &point, vector<double> &line );
};

#endif // SUITPATHFINDER_AI_H