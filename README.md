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
---
METHOD onactionbutton_modif .

  DATA: lt_selected TYPE wdr_context_element_set,
        lo_node     TYPE REF TO if_wd_context_node,
        lo_element  TYPE REF TO if_wd_context_element,
        ls_flight   TYPE sflight.

  " Obtener el nodo de la tabla ALV principal
  lo_node = wd_context->get_child_node( name = wd_this->wdctx_datos ).
  lt_selected = lo_node->get_selected_elements( ).

  " Validar si se ha seleccionado al menos una fila
  IF lines( lt_selected ) EQ 0.
    MESSAGE 'Seleccione al menos una línea para modificar' TYPE 'E'.
    RETURN.
  ENDIF.

  " Limpiar datos previos del nodo de edicion
  wd_context->get_child_node( name = wd_this->wdctx_datos_edit )->invalidate( ).

  " Copiar los datos seleccionados a la vista de edición
  LOOP AT lt_selected INTO lo_element.
    lo_element->get_static_attributes( IMPORTING static_attributes = ls_flight ).
    wd_context->get_child_node( name = wd_this->wdctx_datos_edit )->bind_element( new_item = ls_flight ).
  ENDLOOP.
  
  " Limpiar nodo de la vista principal para que se recargue vacío
  wd_comp_controller->get_node_->invalidate( ).
  " Moverse entre vistas
  wd_this->fire_out_vista_sec_plg( ).
  -----
  METHOD onactionbutton_borrar .

  DATA: lo_node  TYPE REF TO if_wd_context_node,
        lt_datos TYPE STANDARD TABLE OF sflight,
        lv_index TYPE i.

  DATA: lt_text TYPE string_table,
        lv_text TYPE string.

  " Obtener el nodo de datos del ALV
  lo_node = wd_context->get_child_node( name = wd_this->wdctx_datos ).

  " Obtener los registros seleccionados
  DATA(lt_sel_elements) = lo_node->get_selected_elements( ).

  " Obtener todos los datos actuales del ALV
  lo_node->get_static_attributes_table( IMPORTING table = lt_datos ).

  IF lt_sel_elements IS NOT INITIAL.

    LOOP AT lt_sel_elements INTO DATA(lo_sel).
      lv_index = lo_sel->get_index( ).
      DELETE lt_datos INDEX lv_index.
    ENDLOOP.

  ENDIF.

  " Reenlazar en tabla
  lo_node->bind_table( lt_datos ).

ENDMETHOD.
-----------
METHOD onactionbutton_borrar .

*  DATA: lo_node  TYPE REF TO if_wd_context_node,
*        lt_datos TYPE STANDARD TABLE OF sflight,
*        lv_index TYPE i.
*
*  DATA: lt_text TYPE string_table,
*        lv_text TYPE string.
*
*  " Obtener el nodo de datos del ALV
*  lo_node = wd_context->get_child_node( name = wd_this->wdctx_datos ).
*
*  " Obtener los registros seleccionados
*  DATA(lt_sel_elements) = lo_node->get_selected_elements( ).
*
*  " Obtener todos los datos actuales del ALV
*  lo_node->get_static_attributes_table( IMPORTING table = lt_datos ).
*
*  IF lt_sel_elements IS NOT INITIAL.
*
*    LOOP AT lt_sel_elements INTO DATA(lo_sel).
*      lv_index = lo_sel->get_index( ).
*      DELETE lt_datos INDEX lv_index.
*    ENDLOOP.
*
*  ENDIF.
*
*  " Reenlazar en tabla
*  lo_node->bind_table( lt_datos ).

  DATA: lo_node         TYPE REF TO if_wd_context_node,
        lt_datos        TYPE STANDARD TABLE OF sflight,
        lv_index        TYPE i,
        lt_text         TYPE string_table,
        lv_text         TYPE string,
        lv_alias_text   TYPE string,
        lv_count        TYPE i,
        lo_window       TYPE REF TO if_wd_window,
        lo_window_mgr   TYPE REF TO if_wd_window_manager,
        lo_cmp_api      TYPE REF TO if_wd_component,
        lo_sel          TYPE REF TO if_wd_context_element,
        lt_sel_elements TYPE wdr_context_element_set.

  " Obtener el nodo de datos del ALV
  lo_node = wd_context->get_child_node( name = wd_this->wdctx_datos ).

  " Obtener elementos seleccionados
  lt_sel_elements = lo_node->get_selected_elements( ).
  lv_count = lines( lt_sel_elements ).

  IF lv_count = 0.
    " Si no hay selección, mostramos mensaje
    MESSAGE 'No ha seleccionado la linea' TYPE 'I'.
    RETURN.
  ENDIF.

  DATA(lv_count_text) = |{ lv_count }|.
  CONCATENATE 'Está a punto de eliminar' lv_count_text 'línia/es. Desea continuar?' INTO lv_text SEPARATED BY space.

  " Obtener el API del componente y el gestor de ventanas
  lo_cmp_api = wd_comp_controller->wd_get_api( ).
  lo_window_mgr = lo_cmp_api->get_window_manager( ).

  " Crear pop-up
  CALL METHOD lo_window_mgr->create_popup_to_confirm
    EXPORTING
      text         = lt_text
      button_kind  = if_wd_window=>co_buttons_yesno
      message_type = if_wd_window=>co_msg_type_question
      close_button = abap_false
    RECEIVING
      result       = lo_window.

  " Botón SÍ
  lo_window->subscribe_to_button_event(
    button         = if_wd_window=>co_button_yes
    action_name    = 'CONFIRMAR_BORRADO'
    action_view    = wd_this->wd_get_api( )
    is_default_button = abap_true ).

  " Botón NO
  lo_window->subscribe_to_button_event(
    button         = if_wd_window=>co_button_no
    action_name    = 'CANCELAR_BORRADO'
    action_view    = wd_this->wd_get_api( ) ).

  " Abrir ventana
  lo_window->open( ).

  -----
  METHOD onactionbutton_modif .

  DATA: lt_selected TYPE wdr_context_element_set,
        lo_node     TYPE REF TO if_wd_context_node,
        lo_element  TYPE REF TO if_wd_context_element,
        ls_flight   TYPE sflight.

  " Obtener el nodo de la tabla ALV principal
  lo_node = wd_context->get_child_node( name = wd_this->wdctx_datos ).
  lt_selected = lo_node->get_selected_elements( ).

  " Validar si se ha seleccionado al menos una fila
  IF lines( lt_selected ) EQ 0.
    MESSAGE 'Seleccione al menos una línea para modificar' TYPE 'E'.
    RETURN.
  ENDIF.

  " Limpiar datos previos del nodo de edicion
  wd_context->get_child_node( name = wd_this->wdctx_datos_edit )->invalidate( ).

  " Copiar los datos seleccionados a la vista de edición
  LOOP AT lt_selected INTO lo_element.
    lo_element->get_static_attributes( IMPORTING static_attributes = ls_flight ).
    wd_context->get_child_node( name = wd_this->wdctx_datos_edit )->bind_element( new_item = ls_flight ).
  ENDLOOP.

  " Moverse entre vistas
  wd_this->fire_out_vista_sec_plg( ).

ENDMETHOD.

----
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

    " Verificar si el registro ya existe
    SELECT SINGLE *
      FROM sflight
      INTO @DATA(ls_existente)
      WHERE carrid EQ @ls_dato-carrid
        AND connid EQ @ls_dato-connid
        AND fldate EQ @ls_dato-fldate.


    IF sy-subrc EQ 0.
      " Registro existe
      MESSAGE |Ya existe un vuelo con la misma clave: { ls_dato-carrid } { ls_dato-connid } { ls_dato-fldate }| TYPE 'E'.
      EXIT.
    ENDIF.

    " Nuevo registro de vuelo
    MODIFY sflight FROM ls_dato.
    IF sy-subrc EQ 0.
      MESSAGE 'Se ha actualizado la tabla sflight' TYPE 'I'.
    ENDIF.

  ENDLOOP.

  COMMIT WORK AND WAIT.

  " Volver a la vista principal
  wd_this->fire_out_vista_sec_back_plg( ).

--------
 DATA: lo_node         TYPE REF TO if_wd_context_node,
        lt_sel_elements TYPE wdr_context_element_set,
        lv_count        TYPE i,
        lt_text         TYPE string_table,
        lv_line         TYPE string,
        lo_window_mgr   TYPE REF TO if_wd_window_manager,
        lo_cmp_api      TYPE REF TO if_wd_component,
        lo_window       TYPE REF TO if_wd_window.

  " Obtener nodo de datos del ALV
  lo_node = wd_context->get_child_node( name = wd_this->wdctx_datos ).

  " Obtener elementos seleccionados
  lt_sel_elements = lo_node->get_selected_elements( ).
  lv_count = lines( lt_sel_elements ).

  " Si no hay selección
  IF lv_count = 0.
    MESSAGE 'No ha seleccionado la línea' TYPE 'I'.
    RETURN.
  ENDIF.

  " Crear texto para mostrar en popup
  lv_line = |Está a punto de eliminar { lv_count } línea/s. Desea continuar?|.
  APPEND lv_line TO lt_text.

  " Obtener la ventana del popUP
  lo_cmp_api = wd_comp_controller->wd_get_api( ).
  lo_window_mgr = lo_cmp_api->get_window_manager( ).

  " Crear popup
  CALL METHOD lo_window_mgr->create_popup_to_confirm
    EXPORTING
      text         = lt_text
      button_kind  = if_wd_window=>co_buttons_yesno
      message_type = if_wd_window=>co_msg_type_question
      close_button = abap_false
    RECEIVING
      result       = lo_window.

  " Confirgurar eventos botones SI y NO
  lo_window->subscribe_to_button_event(
    button        = if_wd_window=>co_button_yes
    action_name   = 'CONFIRMAR_BORRADO'
    action_view   = wd_this->wd_get_api( )
    is_default_button = abap_true ).

  lo_window->subscribe_to_button_event(
    button        = if_wd_window=>co_button_no
    action_name   = 'CANCELAR_BORRADO'
    action_view   = wd_this->wd_get_api( ) ).

  " Abrir ventana popup
  lo_window->open( ).

  ----------
  METHOD wddoinit .

  DATA: lo_cmp_usage           TYPE REF TO if_wd_component_usage,
        lo_salv_wd_table       TYPE REF TO iwci_salv_wd_table,
        lo_column_settings     TYPE REF TO if_salv_wd_column_settings,
        lo_column              TYPE REF TO cl_salv_wd_column,
        lt_column              TYPE salv_wd_t_column_ref,
        ls_column              TYPE salv_wd_s_column_ref,
        lo_column_header       TYPE REF TO cl_salv_wd_column_header,
        lr_config              TYPE REF TO cl_salv_wd_config_table,
        lo_config              TYPE REF TO cl_salv_wd_config_table,
        lo_input_field         TYPE REF TO cl_salv_wd_uie_input_field,
        l_table                TYPE salv_t_column_ref,
        lo_interfacecontroller TYPE REF TO iwci_salv_wd_table,
        lr_column_settings     TYPE REF TO if_salv_wd_column_settings,
        lt_columns             TYPE        salv_wd_t_column_ref.


  " Obtener componente ALV
  lo_cmp_usage = wd_this->wd_cpuse_alv_edicion( ).

  IF lo_cmp_usage->has_active_component( ) IS INITIAL.
    lo_cmp_usage->create_component( ).
  ENDIF.

  " Obtener el interface controller del ALV
  lo_interfacecontroller = wd_this->wd_cpifc_alv_edicion( ).

  lo_interfacecontroller->set_data( wd_context->get_child_node( wd_this->wdctx_datos_edit ) ).

  " Obtener el modelo de configuración
  lr_config = lo_interfacecontroller->get_model( ).

  " Habilitar modo editable en la tabla
  lr_config->if_salv_wd_table_settings~set_read_only( abap_false ).

  " Obtener configuración de columnas
  lr_column_settings ?= lr_config.
  lt_columns = lr_column_settings->get_columns( ).


  LOOP AT lt_columns INTO ls_column.
    CREATE OBJECT lo_input_field
      EXPORTING
        value_fieldname = ls_column-id.

    CASE ls_column-id.
        " Configurar todos los campos del ALV

      WHEN 'MANDT'.
        ls_column-r_column->set_position( 1 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Mandante' ).

      WHEN 'CARRID'. " Campo clave
        ls_column-r_column->set_position( 2 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Compañia aérea' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'CONNID'. " Campo clave
        ls_column-r_column->set_position( 3 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Cod. conexión de vuelo directo' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'FLDATE'.
        ls_column-r_column->set_position( 4 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Fecha de vuelo' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'PRICE'.
        ls_column-r_column->set_position( 5 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Precio del vuelo' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'CURRENCY'.
        ls_column-r_column->set_position( 6 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Moneda local de la compañía aérea' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'PLANETYPE'.
        ls_column-r_column->set_position( 7 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Tipo de avión' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'SEATSMAX'.
        ls_column-r_column->set_position( 8 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Ocupación máxima en clase económica' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'SEATSOCC'.
        ls_column-r_column->set_position( 9 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Plazas ocupadas en clase económica' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'PAYMENTSUM'.
        ls_column-r_column->set_position( 10 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Total reservas efectuadas hasta el momento' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'SEATSMAX_B'.
        ls_column-r_column->set_position( 11 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Ocupación máxima en clase Business' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'SEATSOCC_B'.
        ls_column-r_column->set_position( 12 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Plazas ocupada en clase Business' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'SEATSMAX_F'.
        ls_column-r_column->set_position( 13 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Ocupación máxima en primera clase' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'SEATSOCC_F'.
        ls_column-r_column->set_position( 14 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Plazas ocupadas en primera clase' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

      WHEN 'EDIT'.
        ls_column-r_column->set_position( 15 ).
        ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Editable' ).

        " Campo editable
        lo_column = lr_column_settings->get_column( ls_column-id ).
        lo_column->set_cell_editor( lo_input_field ).

    ENDCASE.
  ENDLOOP.

ENDMETHOD.

---------------
METHOD wddoinit .

  DATA: lo_cmp_usage           TYPE REF TO if_wd_component_usage,
        lo_salv_wd_table       TYPE REF TO iwci_salv_wd_table,
        lo_column_settings     TYPE REF TO if_salv_wd_column_settings,
        lo_column              TYPE REF TO cl_salv_wd_column,
        lt_column              TYPE salv_wd_t_column_ref,
        ls_column              TYPE salv_wd_s_column_ref,
        lo_column_header       TYPE REF TO cl_salv_wd_column_header,
        lr_config              TYPE REF TO cl_salv_wd_config_table,
        lo_config              TYPE REF TO cl_salv_wd_config_table,
        lo_input_field         TYPE REF TO cl_salv_wd_uie_input_field,
        l_table                TYPE salv_t_column_ref,
        lo_interfacecontroller TYPE REF TO iwci_salv_wd_table,
        lr_column_settings     TYPE REF TO if_salv_wd_column_settings,
        lt_columns             TYPE        salv_wd_t_column_ref,
        lo_nd_data_modif       TYPE REF TO if_wd_context_node.

  DATA: lv_modo_creacion TYPE abap_bool.

  lv_modo_creacion = wd_comp_controller->modo_creacion.

  " Creamos el componente ALV
  lo_cmp_usage = wd_this->wd_cpuse_alv_edicion( ).

  " Si no está creado, lo creamos
  IF lo_cmp_usage->has_active_component( ) IS INITIAL.
    lo_cmp_usage->create_component( ).
  ENDIF.

  " Recuperamos el componente ALV
  lo_salv_wd_table = wd_this->wd_cpifc_alv_edicion( ).
  lo_salv_wd_table->set_data( EXPORTING r_node_data = lo_nd_data_modif ).

  lr_config = lo_salv_wd_table->get_model( ).
  lr_config->if_salv_wd_table_settings~set_cell_action_event_enabled( abap_true ).
  lr_config->if_salv_wd_table_settings~set_selection_mode( value = cl_wd_table=>e_selection_mode-none ).
  lr_config->if_salv_wd_table_settings~set_read_only( abap_false ).
  lr_config->if_salv_wd_table_settings~set_enabled( value = abap_true ).
  lr_config->if_salv_wd_table_settings~set_cell_action_event_enabled( abap_true ).

  " Obtener configuración de columnas
  lr_column_settings ?= lr_config.
  lt_columns = lr_column_settings->get_columns( ).


  LOOP AT lt_columns INTO ls_column.
    CREATE OBJECT lo_input_field EXPORTING value_fieldname = ls_column-id.

    IF lv_modo_creacion EQ abap_true.
      CASE ls_column-id.
         
          " Configurar todos los campos del ALV
        WHEN 'MANDT'.
          ls_column-r_column->set_position( 1 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Mandante' ).

        WHEN 'CARRID'. " Campo clave
          ls_column-r_column->set_position( 2 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Compañia aérea' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'CONNID'. " Campo clave
          ls_column-r_column->set_position( 3 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Cod. conexión de vuelo directo' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'FLDATE'.
          ls_column-r_column->set_position( 4 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Fecha de vuelo' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'PRICE'.
          ls_column-r_column->set_position( 5 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Precio del vuelo' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'CURRENCY'.
          ls_column-r_column->set_position( 6 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Moneda local de la compañía aérea' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'PLANETYPE'.
          ls_column-r_column->set_position( 7 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Tipo de avión' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSMAX'.
          ls_column-r_column->set_position( 8 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Ocupación máxima en clase económica' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSOCC'.
          ls_column-r_column->set_position( 9 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Plazas ocupadas en clase económica' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'PAYMENTSUM'.
          ls_column-r_column->set_position( 10 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Total reservas efectuadas hasta el momento' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSMAX_B'.
          ls_column-r_column->set_position( 11 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Ocupación máxima en clase Business' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSOCC_B'.
          ls_column-r_column->set_position( 12 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Plazas ocupada en clase Business' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSMAX_F'.
          ls_column-r_column->set_position( 13 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Ocupación máxima en primera clase' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSOCC_F'.
          ls_column-r_column->set_position( 14 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Plazas ocupadas en primera clase' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'EDIT'.
          ls_column-r_column->set_position( 15 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Editable' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

      ENDCASE.
    ELSE.
      CASE ls_column-id.
          
          " Configurar todos los campos del ALV
        WHEN 'MANDT'.
          ls_column-r_column->set_position( 1 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Mandante' ).

        WHEN 'CARRID'. " Campo clave
          ls_column-r_column->set_position( 2 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Compañia aérea' ).

          " Campo editable
*        lo_column = lr_column_settings->get_column( ls_column-id ).
*        lo_column->set_cell_editor( lo_input_field ).

        WHEN 'CONNID'. " Campo clave
          ls_column-r_column->set_position( 3 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Cod. conexión de vuelo directo' ).

          " Campo editable
*        lo_column = lr_column_settings->get_column( ls_column-id ).
*        lo_column->set_cell_editor( lo_input_field ).

        WHEN 'FLDATE'.
          ls_column-r_column->set_position( 4 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Fecha de vuelo' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'PRICE'.
          ls_column-r_column->set_position( 5 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Precio del vuelo' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'CURRENCY'.
          ls_column-r_column->set_position( 6 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Moneda local de la compañía aérea' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'PLANETYPE'.
          ls_column-r_column->set_position( 7 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Tipo de avión' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSMAX'.
          ls_column-r_column->set_position( 8 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Ocupación máxima en clase económica' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSOCC'.
          ls_column-r_column->set_position( 9 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Plazas ocupadas en clase económica' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'PAYMENTSUM'.
          ls_column-r_column->set_position( 10 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Total reservas efectuadas hasta el momento' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSMAX_B'.
          ls_column-r_column->set_position( 11 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Ocupación máxima en clase Business' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSOCC_B'.
          ls_column-r_column->set_position( 12 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Plazas ocupada en clase Business' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSMAX_F'.
          ls_column-r_column->set_position( 13 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Ocupación máxima en primera clase' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'SEATSOCC_F'.
          ls_column-r_column->set_position( 14 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Plazas ocupadas en primera clase' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

        WHEN 'EDIT'.
          ls_column-r_column->set_position( 15 ).
          ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
          lo_column_header = ls_column-r_column->get_header( ).
          lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
          lo_column_header->set_text( 'Editable' ).

          " Campo editable
          lo_column = lr_column_settings->get_column( ls_column-id ).
          lo_column->set_cell_editor( lo_input_field ).

      ENDCASE.
    ENDIF.

  ENDLOOP.

ENDMETHOD.

-------
Report de prueba
*&---------------------------------------------------------------------*
*& Include          Z_REPORT_FICH_ABM_FRM
*&---------------------------------------------------------------------*
*&---------------------------------------------------------------------*
*& Form F_INICIALIZAR
*&---------------------------------------------------------------------*
*& Limpiar variables, tablas, estructuras..
*&---------------------------------------------------------------------*
FORM f_inicializar .
  CLEAR: gt_sflight,
         gs_sflight.
ENDFORM.
*&---------------------------------------------------------------------*
*& Form F_SELECCION_DATOS
*&---------------------------------------------------------------------*
*& Seleccion de datos para introducir en tabla.
*&---------------------------------------------------------------------*
FORM f_seleccion_datos .

* Select para sacar los datos de la tabla SFLIGHT
  SELECT carrid connid fldate price planetype
    FROM sflight
    INTO TABLE gt_sflight
    WHERE carrid IN s_carr OR
          connid IN s_conn OR
          fldate IN s_fldate.

  IF sy-subrc EQ 0.
    " Ordenamos por lo campos de filtro
    SORT gt_sflight BY carrid connid fldate.
    DELETE ADJACENT DUPLICATES FROM gt_sflight COMPARING carrid connid fldate.
  ENDIF.

ENDFORM.
*&---------------------------------------------------------------------*
*& Form F_GENERAR_FICHERO
*&---------------------------------------------------------------------*
*& Generación de fichero para tabla SFLIGHT
*&---------------------------------------------------------------------*
FORM f_generar_fichero .
ENDFORM.

...
*&---------------------------------------------------------------------*
*& Include          Z_REPORT_FICH_ABM_SEL
*&---------------------------------------------------------------------*
* PANTALLA DE SELECCIÓN
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
PARAMETERS: p_fich TYPE string. "OBLIGATORY.
SELECT-OPTIONS: s_carr FOR sflight-carrid,
                s_conn FOR sflight-connid,
                s_fldate FOR sflight-fldate.
SELECTION-SCREEN END OF BLOCK b1.
---
FORM generar_fichero .

  CONSTANTS: lc_nomf TYPE string VALUE ''.

  DATA: lv_file    TYPE string,
        lv_nombref TYPE string,
        lv_ruta    TYPE string,
        lv_txt     TYPE string,
        lv_length  TYPE i,
        lv_message TYPE string.

  DATA: lt_file_write     TYPE TABLE OF ty_user_var,
        ls_file_write     LIKE LINE OF  lt_file_write,
        ls_organizaciones TYPE ty_user_var.

  DATA: ls_coordinador_orgunit TYPE ty_coordinador_orgunit.
* INI DGL 06.05.2024 - Cambios extractores de usuarios VAR y CIR.
  DATA: lo_table_desc TYPE REF TO cl_abap_tabledescr,
        lo_descr_ref  TYPE REF TO cl_abap_structdescr.

  FIELD-SYMBOLS: <lfs_field> TYPE any.
* FIN DGL 06.05.2024 - Cambios extractores de usuarios VAR y CIR.
  DATA: lv_period_year TYPE zgrc_sap_period_year,
        lv_day         TYPE num2.

  CLEAR lv_nombref.

  IF p_fich IS NOT INITIAL.
    lv_nombref = p_fich.
  ELSE.
    lv_nombref = lc_nomf.
  ENDIF.

  DESCRIBE FIELD ls_file_write LENGTH lv_length IN CHARACTER MODE.

  PERFORM constantes CHANGING lv_ruta lv_txt .

  CONCATENATE  lv_ruta lv_nombref sy-datum lv_txt INTO lv_file.

  OPEN DATASET lv_file FOR OUTPUT IN LEGACY TEXT MODE CODE PAGE '1160'.  "ENCODING DEFAULT.

  IF sy-subrc NE 0 .                          "Error al crear el fichero
    MESSAGE e000(38) WITH TEXT-004.

  ELSE.

    LOOP AT gt_organizaciones INTO ls_organizaciones.

      MOVE-CORRESPONDING ls_organizaciones TO ls_file_write.
* INI DGL 06.05.2024 - Cambios extractores de usuarios VAR y CIR.
      " Recuperamos la estructura del fichero
      lo_table_desc ?= cl_abap_typedescr=>describe_by_data( gt_organizaciones ).
      lo_descr_ref  ?= lo_table_desc->get_table_line_type( ).

      " Eliminamos las tildes
      LOOP AT lo_descr_ref->components INTO DATA(ls_component).

        ASSIGN COMPONENT ls_component-name OF STRUCTURE ls_file_write TO <lfs_field>.
        IF sy-subrc IS INITIAL AND ls_component-type_kind EQ 'C'.
          REPLACE: ALL OCCURRENCES OF 'á' IN <lfs_field> WITH 'a',
                   ALL OCCURRENCES OF 'Á' IN <lfs_field> WITH 'A',
                   ALL OCCURRENCES OF 'é' IN <lfs_field> WITH 'e',
                   ALL OCCURRENCES OF 'É' IN <lfs_field> WITH 'E',
                   ALL OCCURRENCES OF 'í' IN <lfs_field> WITH 'i',
                   ALL OCCURRENCES OF 'I' IN <lfs_field> WITH 'I',
                   ALL OCCURRENCES OF 'ó' IN <lfs_field> WITH 'o',
                   ALL OCCURRENCES OF 'Ó' IN <lfs_field> WITH 'O',
                   ALL OCCURRENCES OF 'ú' IN <lfs_field> WITH 'u',
                   ALL OCCURRENCES OF 'Ú' IN <lfs_field> WITH 'U'.

        ENDIF.

      ENDLOOP.
* FIN DGL 06.05.2024 - Cambios extractores de usuarios VAR y CIR.
      TRY.

          TRANSFER ls_file_write TO lv_file LENGTH lv_length.
          CLEAR: ls_file_write.
        CATCH cx_sy_conversion_codepage.
          WRITE: TEXT-005, ls_file_write-objid, /.

      ENDTRY.

    ENDLOOP.

  ENDIF.

  lv_message = TEXT-003. "Fichero exportado: &1 Longitud de línea:

  REPLACE '&1' WITH lv_file INTO lv_message.
  WRITE: lv_message, lv_length.

  CLOSE DATASET lv_file.

ENDFORM.
----
*&---------------------------------------------------------------------*
*& Include          ZBIGDATA_CIR_MODOBJ_F01
*&---------------------------------------------------------------------*
*&---------------------------------------------------------------------*
*& Form F_INICIALIZAR
*&---------------------------------------------------------------------*
*& Borrar tablas, estructuras iniciales..
*&---------------------------------------------------------------------*
FORM f_inicializar .
  CLEAR: gt_datos_eval[],
         gt_workflow[],
         gt_preg_resp[].
ENDFORM.

*&---------------------------------------------------------------------*
*& Form F_SELECCION_DATOS
*&---------------------------------------------------------------------*
*& Selección de datos.
*&---------------------------------------------------------------------*
FORM f_seleccion_datos .

  CONSTANTS: lc_svy_type TYPE string VALUE 'Z4',
             lc_wi_type  TYPE string VALUE 'W'.

* PRIMERA SELECT: para los datos de evaluación.
  SELECT a~svyinstid, b~svytmplid,
         b~objectid, b~regulation,
         c~timeframe, c~tf_year, c~date_begin,
         c~date_end, d~taskplan_grp_nam
     INTO TABLE @gt_datos_eval
     FROM grfntsvyinst AS a
     INNER JOIN grfntsvygroup AS b ON
                b~svygrpid EQ a~svygrpid
     INNER JOIN grfntaskplan AS c
                ON c~taskplan_id EQ b~taskplanid
     INNER JOIN grfntaskplangrp AS d
                ON d~taskplan_grp_id EQ c~taskplan_grp_id
     WHERE b~svy_type EQ @lc_svy_type.

  IF sy-subrc EQ 0.
* SEGUNDA SELECT: para el estado, responsable y fecha fin del workflow.
    SELECT
        a~svyinstid,
        b~top_wi_id,
        c~wi_stat,
        c~wi_cd,
        c~wi_aagent,
        c~crea_tmp
      INTO TABLE @gt_workflow
      FROM grfntsvyinst AS a
      INNER JOIN sww_wi2obj AS b ON
          b~instid EQ a~svyinstid
      INNER JOIN swwwihead AS c  ON
          c~top_wi_id EQ b~top_wi_id
      WHERE c~wi_type EQ @lc_wi_type.

    IF sy-subrc EQ 0.
      SORT gt_workflow BY crea_tmp DESCENDING.
    ENDIF.
  ENDIF.

  " TERCERA SELECT: Preguntas y respuestas
  SELECT
     a~svyinstid,
     b~svytmplid,
     c~text,
     d~text,
     e~comments
     INTO TABLE @gt_preg_resp
     FROM grfntsvyinst AS a
     INNER JOIN grfntsvygroup AS b ON
               b~svygrpid EQ a~svygrpid
     INNER JOIN grpcsquestions AS f    ON
               f~survey_id EQ b~svytmplid
     INNER JOIN grpcqlibrary_t AS c ON
               c~question_id EQ f~question_id
     INNER JOIN grpcqanswer AS e ON
               e~survey_id EQ a~svyinstid
     INNER JOIN grfnqlibchoicet AS d ON
               d~question_id EQ e~qid AND
               d~cust_choice EQ e~cust_choice
     WHERE b~svy_type EQ @lc_svy_type.

    IF sy-subrc EQ 0.
    ENDIF.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form F_GENERAR_FICHERO
*&---------------------------------------------------------------------*
*& Generación del fichero.
*&---------------------------------------------------------------------*
FORM f_generar_fichero .

ENDFORM.

