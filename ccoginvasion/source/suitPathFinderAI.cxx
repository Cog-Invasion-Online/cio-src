/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file suitPathFinderAI.cxx
 * @author Brian Lach
 * @date 2017-03-03
 */

#include "suitPathFinderAI.h"

#include <cmath>

#define PI (4 * atan(1.0))

AStarVertex::
AStarVertex(const LVector2f &vert) :
  _do_extrusion(false),
  _has_interior_angle(false) {
  _pos = vert;
}

void AStarVertex::
link(AStarVertex *nbr) {
  add_neighbor(nbr);
  nbr->add_neighbor(this);
}

void AStarVertex::
unlink(AStarVertex *nbr) {
  remove_neighbor(nbr);
  nbr->remove_neighbor(this);
}

void AStarVertex::
unlink_all() {
  vector<AStarVertex *> neighbors = vector<AStarVertex *>(_neighbors);
  for (size_t i = 0; i < neighbors.size(); i++) {
    unlink(neighbors[i]);
  }
}

void AStarVertex::
reset_neighbors() {
  _neighbors.clear();
}

void AStarVertex::
add_neighbor(AStarVertex *nbr) {
  if (find(_neighbors.begin(), _neighbors.end(), nbr) == _neighbors.end()) {
    _neighbors.push_back(nbr);
  }
}

void AStarVertex::
remove_neighbor(AStarVertex *nbr) {
  if (find(_neighbors.begin(), _neighbors.end(), nbr) != _neighbors.end()) {
    _neighbors.erase(find(_neighbors.begin(), _neighbors.end(), nbr));
  }
}

void AStarVertex::
set_polygonal_neighbors(AStarVertex *prev, AStarVertex *next) {
  LVector2f vectoprev = prev->get_pos() - _pos;
  LVector2f vectonext = next->get_pos() - _pos;

  // Find the angle and convert it to an unsigned angle.
  float angle = fmod(vectoprev.signed_angle_deg(vectonext), 360);

  _prev_poly_nbr = prev;
  _next_poly_nbr = next;
  _has_interior_angle = true;
  _interior_angle = angle;

  float prevangle = LVector2f(1, 0).signed_angle_deg(vectoprev);
  float extrudeangle = prevangle + _interior_angle / 2.0 + 180;
  extrudeangle *= PI / 180; // Degrees to radians

  _do_extrusion = true;

  _extrude_vector = LVector2f(cos(extrudeangle), sin(extrudeangle));
}

bool AStarVertex::
is_vertex_inside_angle(AStarVertex *other) const {
  if (_prev_poly_nbr == NULL || !_has_interior_angle) {
    // We are a single vertex, not part of a polygon. Nothing can be
    // "inside" the angle.
    return false;
  }

  LVector2f vectoprev = _prev_poly_nbr->get_pos() - _pos;
  LVector2f vectoother = other->get_pos() - _pos;

  // Find the angle and convert it to an unsigned angle.
  float angle = fmod(vectoprev.signed_angle_deg(vectoother), 360);

  // 'angle' represents the degrees CCW from the vectoprev, while
  // _interior_angle represents the overall degrees CCW that our corner
  // has (and it may be >180 if this is a concave angle). Therefore, if the
  // 'other' vertex is inside our interior angle, angle < _interior_angle.
  return angle < _interior_angle;
}

bool AStarVertex::
is_vertex_inside_opposite(AStarVertex *other) const {
  if (_prev_poly_nbr == NULL || !_has_interior_angle) {
    // We are a single vertex, not part of a polygon. Nothing can be
    // "inside" the angle.
    return false;
  }

  LVector2f vectoprev = _prev_poly_nbr->get_pos() - _pos;
  LVector2f vectoother = other->get_pos() - _pos;

  // Find the angle, spin it around to test the opposite, and convert to an unsigned angle.
  float angle = fmod(vectoprev.signed_angle_deg(vectoother) - 180, 360);

  return angle < _interior_angle;
}

void AStarVertex::
extrude_vertex(float distance) {
  // Push the vertex outward from the center of the geometry it contains.
  if (!_do_extrusion) {
    return; // Cannot extrude this, not part of a polygon!
  }

  _pos += _extrude_vector * distance;
}

bool AStarVertex::
is_vertex_polygonal_neighbor(AStarVertex *other) const {
  return (other == _prev_poly_nbr || other == _next_poly_nbr);
}

float AStarVertex::
get_interior_angle() const {
  return _interior_angle;
}

LVector2f AStarVertex::
get_pos() const {
  return _pos;
}

// The 3 functions arequired by AStarSearch:
vector<AStarVertex *> AStarVertex::
get_neighbors() const {
  return _neighbors;
}

float AStarVertex::
get_heuristic_to(AStarVertex *other) const {
  return (_pos - other->get_pos()).length();
}

float AStarVertex::
get_cost_to(AStarVertex *other) const {
  return (_pos - other->get_pos()).length();
}

//////////////////////////////////////////////////////////////////////////////

AStarPath::
AStarPath(AStarPath *p, AStarVertex *v, double h, double tc) :
  parent(p), vertex(v), heuristic(h), total_cost(tc) {
}

//////////////////////////////////////////////////////////////////////////////

AStarSearch::
AStarSearch() :
  _to_vert(NULL) {
}

AStarSearch::SearchResult AStarSearch::
search(AStarVertex *fromvert, AStarVertex *tovert) {
  _open_list.clear();
  _open_list.push_back(new AStarPath(NULL, fromvert, 0, 0));
  _closed_list.clear();

  _to_vert = tovert;
  while (_open_list.size() > (size_t)0 && _paths.find(tovert) == _paths.end()) {
    do_iteration();
  }

  SearchResult result;

  // Did we find something?
  AStarPath *path = _paths[tovert];
  if (path == NULL) {
    // We failed. And the test will be terminated.
    result.success = false;
  } else {
    // We found a path!
    result.success = true;
    result.pathverts = get_vertices_to_path(path);
  }

  return result;
}

void AStarSearch::
do_iteration() {
  PT(AStarPath) path = _open_list[0];
  _open_list.erase(_open_list.begin());
  AStarVertex *vertex = path->vertex;
  _closed_list.insert(vertex);

  vector<AStarVertex *> neighbors = vertex->get_neighbors();
  for (size_t i = 0; i < neighbors.size(); i++) {
    AStarVertex *neighbor = neighbors[i];
    if (_closed_list.find(neighbor) != _closed_list.end()) {
      // We've already visited this neighbor; ignore.
      continue;
    }

    double cost = vertex->get_cost_to(neighbor) + path->total_cost;

    if (_paths.find(neighbor) != _paths.end()) {
      // There's already a path to this neighbor (i.e. they are
      // probably already on the open list) so we'll see if our
      // path's cost better, and replace it if so.
      PT(AStarPath) neighborpath = _paths[neighbor];
      if (cost < neighborpath->total_cost) {
        // Yes, we're cheaper!
        _open_list.erase(find(_open_list.begin(), _open_list.end(), neighborpath));
        _paths.erase(_paths.find(neighbor));
      } else {
        // No, we're the same or more expensive; ignore this
        // neighbor.
        continue;
      }
    }

    PT(AStarPath) newpath = new AStarPath(path, neighbor, cost, neighbor->get_heuristic_to(_to_vert));
    _paths[neighbor] = newpath;

    vector<PT(AStarPath)>::iterator where = lower_bound(_open_list.begin(), _open_list.end(), newpath);
    _open_list.insert(where, newpath);
  }
}

vector<AStarVertex *> AStarSearch::
get_vertices_to_path(AStarPath *path) {
  // Traces backwards along all of the path's parents to build up a forward list
  // of vertices to visit along the path.
  vector<AStarVertex *> result;
  while (path != NULL) {
    result.insert(result.begin(), path->vertex);
    path = path->parent;
  }
  return result;
}


////////////////////////////////////////////////////////////////////////////////////

#define VERTEX_EXTRUSION .15

SuitPathFinderAI::
SuitPathFinderAI(PyObject *polys) {
  if (polys != (PyObject *)NULL) {
    Py_ssize_t len = PyList_Size(polys);
    for (Py_ssize_t i = 0; i < len; i++) {
      PyObject *points = PyList_GetItem(polys, i);
      add_polygon(points);
    }
    build_neighbors();
  }
}

void SuitPathFinderAI::
add_polygon(PyObject *points) {
  vector<AStarVertex *> new_verts;

  Py_ssize_t len = PyList_Size(points);
  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject *vert = PyList_GetItem(points, i);
    PyObject *prevvert = PyList_GetItem(points, i - 1);
    double x = PyFloat_AsDouble(PyTuple_GetItem(vert, 0));
    double y = PyFloat_AsDouble(PyTuple_GetItem(vert, 1));

    double x2 = PyFloat_AsDouble(PyTuple_GetItem(prevvert, 0));
    double y2 = PyFloat_AsDouble(PyTuple_GetItem(prevvert, 1));

    // Add a boundary line from the previous to here.
    BorderPoints bp;
    bp.push_back(x2);
    bp.push_back(y2);
    bp.push_back(x);
    bp.push_back(y);
    _borders.push_back(bp);

    // Create our vertex.
    PT(AStarVertex) vertex = new AStarVertex(LVector2f(x, y));
    _vertices.push_back(vertex);
    new_verts.push_back(vertex);
  }

  // Now set up the polygonal neighbors on all vertices:
  for (size_t i = 0; i < new_verts.size(); i++) {
    AStarVertex *vert = new_verts[i];
    AStarVertex *prevvert = new_verts[i - 1];
    AStarVertex *nextvert = new_verts[(i + 1) % new_verts.size()];

    vert->set_polygonal_neighbors(prevvert, nextvert);
    vert->extrude_vertex(VERTEX_EXTRUSION);

    if (vert->get_interior_angle() > 180) {
      // This vertex in concave. Nohting is ever going to *walk to* it
      // in order to go somewhere else, so we can actually exclude it
      // from the pathfinding system.
      _vertices.erase(find(_vertices.begin(), _vertices.end(), vert));
    }
  }
}

void SuitPathFinderAI::
build_neighbors() {
  // First reset all vertex neighbors.
  for (size_t i = 0; i < _vertices.size(); i++) {
    _vertices[i]->reset_neighbors();
  }

  // Now we test every vertex pair for visibility to each other:
  for (size_t i = 0; i < _vertices.size(); i++) {
    AStarVertex *v1 = _vertices[i];
    for (size_t j = i + 1; j < _vertices.size(); j++) {
      AStarVertex *v2 = _vertices[j];
      consider_link(v1, v2);
    }
  }
}

PyObject *SuitPathFinderAI::
plan_path(PyObject *from, PyObject *to, float close_enough) {
  // Find a path from "from" to "to", and return it as a series of
  // waypoints (including "to", excluding "from").
  // If a direct path exists, this will simply return [to].
  // If no direct path exists, the pathfinder will use the A* algorithm to
  // generate a path linking the two points.
  // If no path is possible, this function returns None.
  //
  // If close_enough is provided, it specifies a radius around toPoint that
  // is considered "close enough" so that, if "to" lies inside an
  // inaccessible location, the pathfinder will look for an approximate
  // destination instead.
  PyObject *result = PyList_New(0);

  double x1 = PyFloat_AsDouble(PyTuple_GetItem(from, 0));
  double y1 = PyFloat_AsDouble(PyTuple_GetItem(from, 1));

  double x2 = PyFloat_AsDouble(PyTuple_GetItem(to, 0));
  double y2 = PyFloat_AsDouble(PyTuple_GetItem(to, 1));

  // See if the from->to path crosses any polygons :
  vector<float> points;
  points.push_back(x1);
  points.push_back(y1);
  points.push_back(x2);
  points.push_back(y2);
  if (!test_line_intersections(points, _borders)) {
    // Nope, we can just go direct!
    PyList_Append(result, to);
    return result;
  }

  // Pathfinding is necessary. First, create the endpoint vertices:
  PT(AStarVertex) fromvert = new AStarVertex(LVector2f(x1, y1));
  PT(AStarVertex) tovert = new AStarVertex(LVector2f(x2, y2));

  // Now create edges for both vertices:
  for (size_t i = 0; i < _vertices.size(); i++) {
    AStarVertex *vertex = _vertices[i];
    consider_link(vertex, fromvert);
    consider_link(vertex, tovert);
  }

  vector<AStarVertex *> temp_verts;
  temp_verts.push_back(fromvert);
  temp_verts.push_back(tovert);
  bool is_approximate = false;

  bool return_result = false;

  try {
    if (tovert->get_neighbors().size() == 0) {
      if (close_enough == 0.0) {
        // tovert is an inaccessible location -- fail.
        throw exception();
      }

      // We're doing approximate pathing -- instead of failing, try to
      // get some "good enough" connections. We do this by creating a
      // temporary vertex on every nearby border and linking those in.
      is_approximate = true;

      float close_enough_sq = close_enough * close_enough;
      for (size_t i = 0; i < _borders.size(); i++) {
        BorderPoints border = _borders[i];
        PPTLResult projresult = project_point_to_line(tovert->get_pos(), border);
        if (!projresult.success) {
          // No projection lies on the line segment.
          continue;
        }

        LVector2f projected = projresult.result;

        if ((projected - tovert->get_pos()).length_squared() > close_enough_sq) {
          // The projection is too far away to consider.
          continue;
        }

        // We have to extrude the projected vertex a little bit, too.
        LVector2f projectiondir = projected - tovert->get_pos();
        projectiondir.normalize();
        projected += projectiondir * VERTEX_EXTRUSION;

        PT(AStarVertex) projvert = new AStarVertex(projected);
        projvert->link(tovert);
        consider_link(fromvert, projvert);
        for (size_t j = 0; j < _vertices.size(); j++) {
          consider_link(_vertices[j], projvert, false);
        }
        temp_verts.push_back(projvert);
      }
    }

    // Run A* search:
    AStarSearch search;
    AStarSearch::SearchResult sresult = search.search(fromvert, tovert);

    if (sresult.success) {
      vector<AStarVertex *> vertpath = sresult.pathverts;

      if (is_approximate) {
        // Approximate paths are approximate -- they can't go all the
        // way to "to".
        vertpath.pop_back();
      }
      for (size_t i = 0; i < vertpath.size(); i++) {
        AStarVertex *vert = vertpath[i];

        // Create a list of x and y of the vertex
        PyObject *poslist = PyList_New(0);
        PyList_Append(poslist, PyFloat_FromDouble(vert->get_pos().get_x()));
        PyList_Append(poslist, PyFloat_FromDouble(vert->get_pos().get_y()));

        // Append the vertex x, y to the result
        PyList_Append(result, poslist);
        
      }
      return_result = true;
    }

  } catch (const exception &) {
  }

  for (size_t i = 0; i < temp_verts.size(); i++) {
    temp_verts[i]->unlink_all();
  }

  if (!return_result) {
    return Py_None;
  }

  return result;
}

SuitPathFinderAI::PPTLResult SuitPathFinderAI::
project_point_to_line(LVector2f &point, vector<double> &line) {
  double x1 = line[0];
  double y1 = line[1];
  double x2 = line[2];
  double y2 = line[3];

  double x = point.get_x();
  double y = point.get_y();

  PPTLResult result;

  LVector2f origin(x1, y1);
  LVector2f vecline = LVector2f(x2, y2) - origin;
  LVector2f vecpoint = LVector2f(x, y) - origin;

  LVector2f projected = vecpoint.project(vecline);
  if (projected.length_squared() > vecline.length_squared()) {
    result.success = false;
  }
  else if (projected.dot(vecline) < 0) {
    result.success = false;
  }
  else {
    result.success = true;
    result.result = origin + projected;
  }
  
  return result;
}

void SuitPathFinderAI::
consider_link(AStarVertex *v1, AStarVertex *v2, bool test_angles) {
  // If the vertices are polygonal neighbors, they should also be
  // edges on the nav graph:
  if (v1->is_vertex_polygonal_neighbor(v2)) {
    v1->link(v2);
    return;
  }

  if (test_angles) {
    // First, test to make sure a link between the vertices would not
    // go across the inside of a polygon (even if there are no line
    // segments in the way)
    if (v1->is_vertex_inside_angle(v2) || v2->is_vertex_inside_angle(v1)) {
      return; // These vertices are not "facing" each other.
    }

    // As an optimization, if either vertex is inside the other's
    // vertically opposite angle, no link between them will ever be
    // used, since neither vertex will obstruct the other.
    if (v1->is_vertex_inside_opposite(v2) || v2->is_vertex_inside_opposite(v1)) {
      return;
    }
  }

  // Now test for intersection with any of the polygon borders:
  float x1 = v1->get_pos().get_x();
  float y1 = v1->get_pos().get_y();

  float x2 = v2->get_pos().get_x();
  float y2 = v2->get_pos().get_y();

  vector<float> points;
  points.push_back(x1);
  points.push_back(y1);
  points.push_back(x2);
  points.push_back(y2);

  if (test_line_intersections(points, _borders)) {
    return; // Nope, a border is in the way!
  }

  // If we made it here, the two vertices can "see" each other and
  // should thus be made neighbors for pathfinding purposes.
  v1->link(v2);
}

SuitPathFinderAI::MLMResult SuitPathFinderAI::
make_line_mat(float x1, float y1, float x2, float y2) {
  // This function generates a transformation matrix to convert coordinates
  // from worldspace to be local to the provided line.
  MLMResult result;

  // This matrix will do the forward transformation.In other words, it
  // transforms (0, 0) -> (x1, y1) and (0, 1) -> (x2, y2)
  // N.B.the notation below is the transpose of the matrix I'm defining,
  // because Panda3D's Mat3 constructor is column-major.
  LMatrix3f mat(y2 - y1, x1 - x2, 0,
                x2 - x1, y2 - y1, 0,
                     x1,      y1, 1);

  // Now we invert it, so that it does what we want: the reverse
  // transformation (i.e. (x1, y1) -> (0, 0) and (x2, y2) -> (0, 1))
  if (!mat.invert_in_place()) {
    // The matrix is singular, which means it has no inverse.
    result.success = false;
  } else {
    result.success = true;
    result.result = mat;
  }

  return result;
}

bool SuitPathFinderAI::
test_line_intersections(vector<float> points, vector<BorderPoints> bords) {
  // Tests if "points" intersects any of the lines in the "bords" list.
  // Each line is a tuple of (x1, y1, x2, y2).

  float x1, y1, x2, y2 = points[0], points[1], points[2], points[3];
  MLMResult matres = make_line_mat(x1, y1, x2, y2);

  if (!matres.success) {
    // The points line is not valid, and so an inverse transformation
    // canot be made. The line is probably 0-length or otherwise
    // cannot intersect anything anyway, so we'll just say it's okay:
    return false;
  }

  LMatrix3f mat = matres.result;

  for (size_t i = 0; i < bords.size(); i++) {
    float x1 = bords[i][0];
    float y1 = bords[i][1];
    float x2 = bords[i][2];
    float y2 = bords[i][3];

    // First, let's transform the endpoints of the line.
    // N.B. this uses homogeneous coordinates, hence the use of
    // 3-dimensional points.
    LVecBase3f xform1 = mat.xform(LVecBase3f(x1, y1, 1));
    LVecBase3f xform2 = mat.xform(LVecBase3f(x2, y2, 1));

    // In order for an intersection to be happening, one point must be
    // on our left (negative X) and one on our right (positive X):
    if (!((xform1.get_x() < 0 && xform2.get_x() > 0) || (xform1.get_x() > 0 && xform2.get_x() < 0))) {
      // This line has both points on one side of us, no intersection
      // is possible. Skip it.
      continue;
    }

    // As the points are on opposite sides, we need to find the line's
    // y-intercept.
    float m = (xform2.get_y() - xform1.get_y()) / (xform2.get_x() - xform1.get_x());
    float b = m * -xform1.get_x() + xform1.get_y();

    // If the y - intercept is between 0 - 1, we have an intersection, as our
    // incident line runs from (0, 0)->(0, 1) in this coordinate space.
    // This is an exclusive range as *grazing* the line (skimming by one
    // of its endpoints) is OK.
    float epsilon = 0.001;
    if (0.0 + epsilon < b < 1.0 - epsilon) {
      return true;
    }
  }

  // The for loop concluded, nothing found.
  return false;
}