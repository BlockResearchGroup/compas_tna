compas\_tna.diagrams.FormDiagram
================================

.. currentmodule:: compas_tna.diagrams

.. autoclass:: FormDiagram

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~FormDiagram.__init__
      ~FormDiagram.add_face
      ~FormDiagram.add_feet
      ~FormDiagram.add_vertex
      ~FormDiagram.anchors
      ~FormDiagram.bbox
      ~FormDiagram.clear
      ~FormDiagram.clear_facedict
      ~FormDiagram.clear_halfedgedict
      ~FormDiagram.clear_vertexdict
      ~FormDiagram.collapse_edge
      ~FormDiagram.collapse_edge_tri
      ~FormDiagram.collapse_small_edges
      ~FormDiagram.copy
      ~FormDiagram.corners
      ~FormDiagram.cull_edges
      ~FormDiagram.cull_vertices
      ~FormDiagram.delete_face
      ~FormDiagram.delete_vertex
      ~FormDiagram.draw
      ~FormDiagram.dual
      ~FormDiagram.dump
      ~FormDiagram.dumps
      ~FormDiagram.edge_coordinates
      ~FormDiagram.edge_direction
      ~FormDiagram.edge_faces
      ~FormDiagram.edge_label_name
      ~FormDiagram.edge_length
      ~FormDiagram.edge_midpoint
      ~FormDiagram.edge_name
      ~FormDiagram.edge_point
      ~FormDiagram.edge_vector
      ~FormDiagram.edges
      ~FormDiagram.edges_on_boundary
      ~FormDiagram.edges_where
      ~FormDiagram.face_adjacency_halfedge
      ~FormDiagram.face_area
      ~FormDiagram.face_center
      ~FormDiagram.face_centroid
      ~FormDiagram.face_coordinates
      ~FormDiagram.face_corners
      ~FormDiagram.face_degree
      ~FormDiagram.face_flatness
      ~FormDiagram.face_halfedges
      ~FormDiagram.face_label_name
      ~FormDiagram.face_max_degree
      ~FormDiagram.face_min_degree
      ~FormDiagram.face_name
      ~FormDiagram.face_neighbors
      ~FormDiagram.face_normal
      ~FormDiagram.face_vertex_ancestor
      ~FormDiagram.face_vertex_descendant
      ~FormDiagram.face_vertices
      ~FormDiagram.faces
      ~FormDiagram.faces_on_boundary
      ~FormDiagram.faces_where
      ~FormDiagram.fixed
      ~FormDiagram.from_data
      ~FormDiagram.from_json
      ~FormDiagram.from_lines
      ~FormDiagram.from_obj
      ~FormDiagram.from_pickle
      ~FormDiagram.from_ply
      ~FormDiagram.from_points
      ~FormDiagram.from_polygons
      ~FormDiagram.from_polyhedron
      ~FormDiagram.from_rhinomesh
      ~FormDiagram.from_stl
      ~FormDiagram.from_vertices_and_faces
      ~FormDiagram.get_any_edge
      ~FormDiagram.get_any_face
      ~FormDiagram.get_any_face_vertex
      ~FormDiagram.get_any_vertex
      ~FormDiagram.get_any_vertices
      ~FormDiagram.get_continuous_edges
      ~FormDiagram.get_edge_attribute
      ~FormDiagram.get_edge_attributes
      ~FormDiagram.get_edges_attribute
      ~FormDiagram.get_edges_attributes
      ~FormDiagram.get_face_attribute
      ~FormDiagram.get_face_attributes
      ~FormDiagram.get_faces_attribute
      ~FormDiagram.get_faces_attributes
      ~FormDiagram.get_parallel_edges
      ~FormDiagram.get_vertex_attribute
      ~FormDiagram.get_vertex_attributes
      ~FormDiagram.get_vertices_attribute
      ~FormDiagram.get_vertices_attributes
      ~FormDiagram.gkey_key
      ~FormDiagram.has_edge
      ~FormDiagram.has_vertex
      ~FormDiagram.index_key
      ~FormDiagram.index_uv
      ~FormDiagram.insert_vertex
      ~FormDiagram.is_edge_on_boundary
      ~FormDiagram.is_manifold
      ~FormDiagram.is_orientable
      ~FormDiagram.is_quadmesh
      ~FormDiagram.is_regular
      ~FormDiagram.is_trimesh
      ~FormDiagram.is_valid
      ~FormDiagram.is_vertex_connected
      ~FormDiagram.is_vertex_on_boundary
      ~FormDiagram.key_gkey
      ~FormDiagram.key_index
      ~FormDiagram.leaves
      ~FormDiagram.load
      ~FormDiagram.loads
      ~FormDiagram.number_of_edges
      ~FormDiagram.number_of_faces
      ~FormDiagram.number_of_vertices
      ~FormDiagram.plot
      ~FormDiagram.residual
      ~FormDiagram.set_edge_attribute
      ~FormDiagram.set_edge_attributes
      ~FormDiagram.set_edges_attribute
      ~FormDiagram.set_edges_attributes
      ~FormDiagram.set_face_attribute
      ~FormDiagram.set_face_attributes
      ~FormDiagram.set_faces_attribute
      ~FormDiagram.set_faces_attributes
      ~FormDiagram.set_vertex_attribute
      ~FormDiagram.set_vertex_attributes
      ~FormDiagram.set_vertices_attribute
      ~FormDiagram.set_vertices_attributes
      ~FormDiagram.smooth
      ~FormDiagram.split_boundary
      ~FormDiagram.split_edge
      ~FormDiagram.split_edge_tri
      ~FormDiagram.split_face
      ~FormDiagram.summary
      ~FormDiagram.swap_edge_tri
      ~FormDiagram.to_data
      ~FormDiagram.to_json
      ~FormDiagram.to_obj
      ~FormDiagram.to_pickle
      ~FormDiagram.to_vertices_and_faces
      ~FormDiagram.unweld_vertices
      ~FormDiagram.update_boundaries
      ~FormDiagram.update_default_edge_attributes
      ~FormDiagram.update_default_face_attributes
      ~FormDiagram.update_default_vertex_attributes
      ~FormDiagram.update_exterior
      ~FormDiagram.update_interior
      ~FormDiagram.uv_index
      ~FormDiagram.vertex_area
      ~FormDiagram.vertex_coordinates
      ~FormDiagram.vertex_degree
      ~FormDiagram.vertex_faces
      ~FormDiagram.vertex_label_name
      ~FormDiagram.vertex_laplacian
      ~FormDiagram.vertex_max_degree
      ~FormDiagram.vertex_min_degree
      ~FormDiagram.vertex_name
      ~FormDiagram.vertex_neighborhood
      ~FormDiagram.vertex_neighborhood_centroid
      ~FormDiagram.vertex_neighbors
      ~FormDiagram.vertex_normal
      ~FormDiagram.vertices
      ~FormDiagram.vertices_on_boundaries
      ~FormDiagram.vertices_on_boundary
      ~FormDiagram.vertices_where
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~FormDiagram.adjacency
      ~FormDiagram.data
      ~FormDiagram.name
   
   