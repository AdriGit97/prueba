# prueba
Prueba de Git para alumno DAM
METHOD zcreate_ovs_filtro_carrid .

  TYPES:
    BEGIN OF lty_stru_input, " filtro
      carrid TYPE s_carr_id,
    END OF lty_stru_input.
  TYPES:
    BEGIN OF lty_stru_list, " Lista del filtro de la tabla
      carrid TYPE s_carr_id,
    END OF lty_stru_list.

  DATA: ls_search_input TYPE lty_stru_input,
        ls_search       TYPE lty_stru_input,
        lt_select_list  TYPE STANDARD TABLE OF lty_stru_list,
        ls_text         TYPE wdr_name_value,
        lt_label_texts  TYPE wdr_name_value_list,
        lt_column_texts TYPE wdr_name_value_list.

  DATA: lo_nd_zwd_filtros TYPE REF TO if_wd_context_node,
        lo_el_zwd_filtros TYPE REF TO if_wd_context_element,
        lo_node_alv       TYPE REF TO if_wd_context_node,
        lt_sflight        TYPE TABLE OF sflight.

  FIELD-SYMBOLS: <ls_query_params>    TYPE lty_stru_input,
                 <ls_selection>       TYPE lty_stru_list,
                 <fs_selection_table> TYPE table.

  CASE ovs_callback_object->phase_indicator.
* Título de la ventana, encabezado de grupo, encabezado de tabla.
    WHEN if_wd_ovs=>co_phase_0.

      " Label
      ls_text-name = 'CARRID'.
      ls_text-value = 'Compañia aérea'.
      INSERT ls_text INTO TABLE lt_label_texts.

      " Las columnas deben coincidir con la estructura de la lista
      " Columnas
      ls_text-name = 'CARRID'.
      ls_text-value = 'Compañia aérea'.
      INSERT ls_text INTO TABLE lt_column_texts.

      ovs_callback_object->set_configuration( label_texts  = lt_label_texts
                                              column_texts = lt_column_texts ).


    WHEN if_wd_ovs=>co_phase_1.
      " Declaracion de busqueda
      CLEAR: ls_search, ls_search_input.

      ovs_callback_object->context_element->get_static_attributes( IMPORTING static_attributes = ls_search_input ).
      ovs_callback_object->set_input_structure( input = ls_search_input ).

    WHEN if_wd_ovs=>co_phase_2.

      DATA(lo_nd_ovs_filters) = wd_context->get_child_node( name = wd_this->wdctx_filtros ).
      DATA(ls_ovs_filters) = VALUE wd_this->element_filtros( ).

      " si el campo CARRID ya tiene un valor en pantalla, necesitamos el carrid para filtrar los resultados.
      lo_nd_ovs_filters->get_static_attributes( IMPORTING static_attributes = ls_ovs_filters ).

      IF ls_ovs_filters-carrid IS NOT INITIAL.
        DELETE lt_sflight WHERE carrid NP ls_ovs_filters-carrid.
      ENDIF.

      " Se trae los datos necesarios de la sflight para tratarlos.
      " Seleccionamos los datos de sflight
      SELECT *
        FROM sflight
        INTO TABLE lt_sflight.

      " Ordenamos y borramos duplicados
      SORT lt_sflight BY carrid.
      DELETE ADJACENT DUPLICATES FROM lt_sflight COMPARING carrid.

      " Introduzco el valor en la tabla que voy a mostrar de la lista con sus datos de carrid y connid
      lt_select_list = VALUE #( FOR ls_datos IN lt_sflight
                      (  carrid = ls_datos-carrid ) ).

      " obtenemos los valores que ha escrito el usuario en la ayuda de busqueda
      ASSIGN ovs_callback_object->query_parameters->* TO <ls_query_params>.

      " Si el filtro recibe un valor de busqueda
      IF <ls_query_params> IS ASSIGNED AND <ls_query_params>-carrid IS NOT INITIAL.
        DELETE lt_select_list WHERE carrid NP <ls_query_params>-carrid.
      ENDIF.

      " Muestra la ayuda de búsqueda en la tabla de resultado
      ovs_callback_object->set_output_table( output = lt_select_list ).

      IF lt_select_list[] IS INITIAL. " Si no tienen ningun registro, error
        MESSAGE e101(zgrc) INTO DATA(lv_msg). " No se han encontrado datos para los criterios seleccionados.
        wd_this->go_message_manager->report_error_message( EXPORTING message_text = lv_msg ).
      ENDIF.

    WHEN if_wd_ovs=>co_phase_3.

      ASSIGN ovs_callback_object->selection->* TO <ls_selection>.
      IF <ls_selection> IS ASSIGNED.
        CLEAR: ls_search.
        ovs_callback_object->context_element->set_attribute(
                               name  = 'CARRID'
                               value = <ls_selection>-carrid ).

      ENDIF.

  ENDCASE.
ENDMETHOD.

***
METHOD wddoinit .

  DATA: lo_cmp_usage       TYPE REF TO if_wd_component_usage,
        lo_salv_wd_table   TYPE REF TO iwci_salv_wd_table,
        lo_column_settings TYPE REF TO if_salv_wd_column_settings,
        lo_column          TYPE REF TO cl_salv_wd_column,
        lt_column          TYPE salv_wd_t_column_ref,
        ls_column          TYPE salv_wd_s_column_ref,
        lo_column_header   TYPE REF TO cl_salv_wd_column_header,
        lr_config          TYPE REF TO cl_salv_wd_config_table,
        lr_input_field     TYPE REF TO cl_salv_wd_uie_input_field,
        l_table            TYPE salv_t_column_ref.

*    Creamos el componente ALV
  lo_cmp_usage = wd_this->wd_cpuse_alv_table( ).

  " Si no está creado, lo creamos
  IF lo_cmp_usage->has_active_component( ) IS INITIAL.
    lo_cmp_usage->create_component( ).
  ENDIF.

  " Recuperamos el componente ALV
  lo_salv_wd_table = wd_this->wd_cpifc_alv_table( ).
  lr_config = lo_salv_wd_table->get_model( ).
  lr_config->if_salv_wd_table_settings~set_cell_action_event_enabled( abap_true ).
  lo_salv_wd_table->get_model( )->if_salv_wd_table_settings~set_visible_row_count( '30' ).
  lo_column_settings ?= lo_salv_wd_table->get_model( ).

  " Recuperamos las columnas
  lt_column = lo_column_settings->get_columns( ).

  LOOP AT lt_column INTO ls_column.
    lo_column = lr_config->if_salv_wd_column_settings~get_column( id = ls_column-id ).
    CASE ls_column-id.
      WHEN 'CARRID'.
        ls_column-r_column->set_cell_editor( value = lr_input_field ).
        lr_input_field->set_read_only_fieldname( value = 'EDIT' ).

      WHEN 'CONNID'.
        ls_column-r_column->set_cell_editor( value = lr_input_field ).
        lr_input_field->set_read_only_fieldname( value = 'EDIT' ).

      WHEN 'PLANETYPE'.
        ls_column-r_column->set_cell_editor( value = lr_input_field ).
        lr_input_field->set_read_only_fieldname( value = 'EDIT' ).
    ENDCASE.
  ENDLOOP.
ENDMETHOD.

-----------
METHOD onactiongrabar .
  DATA: lt_datos_edit           TYPE TABLE OF sflight,
        ls_dato                 TYPE sflight,
        lo_nd_datos             TYPE REF TO if_wd_context_node,
        lo_nd_datos_edit        TYPE REF TO if_wd_context_node,
        lv_msg                  TYPE string,
        ls_existente            TYPE sflight,
        lo_cmp_usage            TYPE REF TO if_wd_component_usage,
        lo_interface_controller TYPE REF TO iwci_salv_wd_table.

* Obtener instancia del componente ALV
  lo_cmp_usage = wd_this->wd_cpuse_alv_table( ).
  IF lo_cmp_usage->has_active_component( ) IS INITIAL.
    lo_cmp_usage->create_component( ).
  ENDIF.

  lo_interface_controller = wd_this->wd_cpifc_alv_table( ).

* Leer los datos del contexto
  lo_nd_datos = wd_context->get_child_node( name = wd_this->wdctx_datos_edit ).

*  " Volver a la vista principal
  wd_this->fire_out_vista_sec_back_plg( ).

* validar y grabar
  LOOP AT lt_datos_edit INTO ls_dato.

* validar campos obligatorios
    IF ls_dato-carrid IS INITIAL OR
       ls_dato-connid IS INITIAL OR
       ls_dato-fldate IS INITIAL.
      lv_msg = |Faltan campos obligatorios en línea { sy-tabix }|.
      MESSAGE lv_msg TYPE 'E'.
      EXIT.
    ENDIF.

* verificar si el registro ya existe en sflight
    SELECT SINGLE *
            FROM sflight
      INTO @ls_existente
      WHERE carrid EQ @ls_dato-carrid
        AND connid EQ @ls_dato-connid
        AND fldate EQ @ls_dato-fldate.

    IF sy-subrc = 0.
      lv_msg = |Ya existe un vuelo con misma clave en línea { sy-tabix }|.
      MESSAGE lv_msg TYPE 'E'.
      EXIT.
    ENDIF.

* insertar nuevo registro
    INSERT sflight FROM ls_dato.
    IF sy-subrc <> 0.
      lv_msg = |Error al insertar en línea { sy-tabix }|.
      MESSAGE lv_msg TYPE 'E'.
      EXIT.
    ENDIF.

  ENDLOOP.

  COMMIT WORK AND WAIT.

ENDMETHOD.

-----------------
METHOD onactiongrabar .
  DATA: lo_nd_datos     TYPE REF TO if_wd_context_node,
        lo_nd_datos_aux TYPE REF TO if_wd_context_node,
        lt_elements     TYPE wdr_context_element_set,
        lo_element      TYPE REF TO if_wd_context_element,
        ls_dato         TYPE sflight.

  " Obtener el nodo
  lo_nd_datos = wd_context->get_child_node( name = wd_this->wdctx_datos_edit ).

  " Hacer un cast a nodo tabla para poder usar get_elements
  lo_nd_datos_aux ?= lo_nd_datos.

  IF lo_nd_datos_aux IS INITIAL.
    MESSAGE 'No existen datos' TYPE 'E'.
    RETURN.
  ENDIF.

  " Obtener todos los elementos
  lt_elements = lo_nd_datos_aux->get_elements( ).

  LOOP AT lt_elements INTO lo_element.
    CLEAR ls_dato.

    " Obtener atributos de cada elemento
    lo_element->get_static_attributes( IMPORTING static_attributes = ls_dato ).

    " Validaciones
    IF ls_dato-carrid IS INITIAL OR
       ls_dato-connid IS INITIAL OR
       ls_dato-fldate IS INITIAL.
      MESSAGE 'Deben estan rellenos los campos son obligatorios' TYPE 'E'.
    ENDIF.

    " Nuevo registro de vuelo
    MODIFY sflight FROM ls_dato.
    IF sy-subrc EQ 0.
      MESSAGE 'Se ha actualizo la tabla sflight' TYPE 'I'.
    ENDIF.

  ENDLOOP.

  COMMIT WORK AND WAIT.

  " Volver a la vista principal
  wd_this->fire_out_vista_sec_back_plg( ).
ENDMETHOD.

----------------
METHOD onactionbutton_buscar .
  DATA: lc_mensaje_error      TYPE string VALUE 'Es necesario rellenar algun campo para filtrar',
        lc_mensaje_error_filt TYPE string VALUE 'No hay datos'.


* Búsqueda por filtros
  DATA: lo_nd_datos            TYPE REF TO if_wd_context_node,
        lo_nd_datos_mod        TYPE REF TO if_wd_context_node,
        lo_nd_el_datos         TYPE REF TO if_wd_context_element,
        lo_nd_el_datos_mod     TYPE REF TO if_wd_context_element,
        ls_datos               TYPE wd_this->elements_datos,
        lt_selecccion_elements TYPE wdr_context_element_set.

**** NODO DE DATOS ****
*  Obtenemos el nombre del nodo de datos, el valor del elemento y atributos
  lo_nd_datos = wd_context->get_child_node( name = wd_this->wdctx_datos ).
  lo_nd_el_datos = lo_nd_datos->get_element( ).

**** NODO DE FILTROS ****
*  " Obtenemos el nombre del nodo de filtros, elementos y atributos
  DATA(lo_nd_filtros) = wd_context->get_child_node( name = wd_this->wdctx_filtros ).
  DATA(ls_filtros) = VALUE wd_this->element_filtros( ).

  lo_nd_filtros->get_static_attributes( IMPORTING static_attributes = ls_filtros ).

  IF ls_filtros-carrid IS INITIAL AND
     ls_filtros-connid IS INITIAL AND
     ls_filtros-planetype IS INITIAL.
    " Mensaje de error: Es necesario rellenar algun campo del filtro
    wd_this->wd_get_api( )->get_message_manager( )->report_error_message( lc_mensaje_error ).
  ENDIF.


*  " SELECCIONES DE DATOS PARA LOS FILTROS
  IF ls_filtros-carrid IS NOT INITIAL AND
     ls_filtros-connid IS INITIAL .

    SELECT *
      FROM sflight
      INTO TABLE @DATA(lt_sf_carrid)
      WHERE carrid EQ @ls_filtros-carrid.
    IF sy-subrc EQ 0.
      lo_nd_datos->bind_table( new_items = lt_sf_carrid set_initial_elements = abap_true ).
    ENDIF.
  ENDIF.

  IF ls_filtros-carrid IS NOT INITIAL AND
     ls_filtros-connid IS NOT INITIAL.

    SELECT *
      FROM sflight
      INTO TABLE @DATA(lt_sf_carr_conn)
      WHERE carrid EQ @ls_filtros-carrid AND
            connid EQ @ls_filtros-connid.

    IF sy-subrc EQ 0.
      lo_nd_datos->bind_table( new_items = lt_sf_carr_conn set_initial_elements = abap_true ).
    ENDIF.

  ENDIF.


  IF ls_filtros-carrid IS NOT INITIAL AND
     ls_filtros-connid IS NOT INITIAL AND
     ls_filtros-planetype IS NOT INITIAL.

    SELECT *
      FROM sflight
      INTO TABLE @DATA(lt_sf_carr_conn_plan)
      WHERE carrid EQ @ls_filtros-carrid AND
            connid EQ @ls_filtros-connid AND
            planetype EQ @ls_filtros-planetype.

    IF sy-subrc EQ 0.
      lo_nd_datos->bind_table( new_items = lt_sf_carr_conn_plan set_initial_elements = abap_true ).
    ENDIF.
  ENDIF.



***** BUSCAR TODA LA TABLA EJERCICIO ANTERIOR:
  " Para buscar toda la tabla.
*  DATA: lo_nd_zwd_formacion_nodo TYPE REF TO if_wd_context_node,
*        lo_el_zwd_formacion_nodo TYPE REF TO if_wd_context_element,
*        lo_node_alv              TYPE REF TO if_wd_context_node.
*        lt_buscar_datos          TYPE TABLE OF wd_this->element_zwd_formacion_nodo.
*
*  " Obtenemos el nodo
*  lo_nd_zwd_formacion_nodo = wd_context->get_child_node( name = wd_this->wdctx_zwd_formacion_nodo ).

*  " Seleccionamos los datos de sflight
*  SELECT *
*    FROM sflight
*    INTO TABLE lt_buscar_datos.
*
*  IF lo_nd_zwd_formacion_nodo IS BOUND.
*    " Pasar los datos al ALV
*    lo_nd_zwd_formacion_nodo->bind_table( new_items = lt_buscar_datos set_initial_elements = abap_true ).
*  ENDIF.
*
*  " Obtener el nodo del ALV
*  lo_node_alv = wd_context->get_child_node( name = wd_this->wdctx_zwd_filtros ).

  " Limpiar datos previos
*  lo_node_alv->invalidate( ).
ENDMETHOD.
