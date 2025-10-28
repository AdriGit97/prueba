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

------------------
CUARTO EXTRACTOR:
FORM seleccion_construccion_datos .
  CONSTANTS: lc_svy_type  TYPE string VALUE 'Z1',
             lc_i         TYPE string VALUE 'I',
             lc_eq        TYPE string VALUE 'EQ',
             lc_bt        TYPE string VALUE 'BT',
             lc_wi_type   TYPE string VALUE 'W',
             lc_completed TYPE string VALUE 'COMPLETED',
             lc_ready     TYPE string VALUE 'READY',
             lc_selected  TYPE string VALUE 'SELECTED',
             lc_cancelled TYPE string VALUE 'CANCELLED'.

  DATA: lr_instid          TYPE RANGE OF grfn_guid,
        lr_wi_rh_task      TYPE RANGE OF sww_task,
        lr_fecha           TYPE RANGE OF sy-datum,
        lt_list            TYPE grfn_t_tf_tframe_list,
        lt_responsables    TYPE TABLE OF swhactor,
        lt_question_answer TYPE grfn_t_api_question_answer,
        lo_object_qsurvey  TYPE REF TO if_grfn_api_survey_resp_cont,
        lo_survey_response TYPE REF TO if_grfn_api_survey_response,
        ls_survey_template TYPE grpc_s_api_survey_data,
        ls_datos           TYPE gty_fichero,
        lv_qsurvey_id      TYPE grfn_api_object_id,
        lv_fecha           TYPE sy-datum.

  go_session = cl_grfn_api_session=>open_daily( ).

  " Obtencion de meses para el campo timeframe periodo.
  CALL METHOD cl_grfn_api_timeframe=>timeframes
    RECEIVING
      rt_list = lt_list.

  lr_wi_rh_task = VALUE #( sign   = lc_i
                           option = lc_eq
                         ( low    = 'TS90100016' )
                         ( low    = 'TS90100013' ) ). " PREGUNTAR A DANI: en que task están éstas.

* AUTOEVALUACIÖN:
  SELECT svyinst~svyinstid, " Id_autoevaluación
         svygroup~objectid, " Sproc_id
         svygroup~svygrpid, " ID grupo de la autoevaluación
         svyinst~completed_at, " Fecha completada de la autoevaluación
         taskplan~timeframe, " Periodo
         taskplan~tf_year,   " Año
         taskplangrp~taskplan_grp_nam, " Tipo_actividad
         svygroup~regulation, " Normativa
         taskplan~date_begin, " Fecha_lanzamiento
         taskplan~date_end,   " Fecha_vencimiento
         svyinst~scomment,    " Comentarios generales
         svyinst~zzcomentario " Comentarios responsable
     INTO TABLE @DATA(lt_datos_eval_cir_subp)
     FROM grfntsvyinst AS svyinst
     INNER JOIN grfntsvygroup AS svygroup ON
                svygroup~svygrpid EQ svyinst~svygrpid
     INNER JOIN grfntaskplan AS taskplan
                ON taskplan~taskplan_id EQ svygroup~taskplanid
     INNER JOIN grfntaskplangrp AS taskplangrp
                ON taskplangrp~taskplan_grp_id EQ taskplan~taskplan_grp_id
     WHERE svygroup~svy_type EQ @lc_svy_type.

  IF sy-subrc EQ 0.
    " Ordenamos las tareas de autoevaluacion por id de grupo y fecha completada,
    " quedando las completadas mas recientemente en primer lugar
    SORT lt_datos_eval_cir_subp BY svygrpid    DESCENDING
                                  completed_at DESCENDING.

    " Borramos los duplicados teniendo en cuenta el ID del grupo
    DELETE ADJACENT DUPLICATES FROM lt_datos_eval_cir_subp COMPARING svygrpid.

    " Rango para los instid
    lr_instid = VALUE #( FOR ls_datos_eval_cir_subp IN lt_datos_eval_cir_subp
                               sign   = lc_i
                               option = lc_eq
                             ( low    = ls_datos_eval_cir_subp-svyinstid ) ).

* DATOS TAREAS DEL WORKFLOW.
    SELECT
     wi2obj~instid,  " Id de la autoevaluación
     swwwihead~top_wi_id, " Id Workflow padre
     swwwihead~wi_id,   " Id workflow item
     swwwihead~wi_stat, " Estado del workflow
     swwwihead~wi_aed,   " Fecha fin
     swwwihead~wi_rh_task, " Tarea
     swwwihead~wi_aagent, " Responsable actual
     swwwihead~crea_tmp  "Para ordenar más reciente
    INTO TABLE @DATA(lt_tareas_wf)
    FROM swwwihead AS swwwihead
    INNER JOIN sww_wi2obj AS wi2obj ON
        wi2obj~top_wi_id EQ swwwihead~top_wi_id
    WHERE swwwihead~wi_type EQ @lc_wi_type AND
        swwwihead~wi_stat  NE @lc_cancelled AND
        wi2obj~instid IN @lr_instid AND
        swwwihead~wi_rh_task IN @lr_wi_rh_task " PREGUNTAR DANI: Si es solo una tarea EQ, si esta comprendido entre varias tareas un rango
      ORDER BY swwwihead~top_wi_id, swwwihead~crea_tmp DESCENDING.

    IF sy-subrc EQ 0.
      DELETE ADJACENT DUPLICATES FROM lt_tareas_wf COMPARING top_wi_id.

      lr_instid = VALUE #( FOR ls_tarea_wf IN lt_tareas_wf
                               sign   = lc_i
                               option = lc_eq
                             ( low    = ls_tarea_wf-instid ) ).

      DELETE lt_datos_eval_cir_subp WHERE svyinstid NOT IN lr_instid.
    ENDIF.

* DATOS TEXTO DE LAS PREGUNTAS.
    SELECT *
      FROM grfnqlibchoicet
      INTO TABLE @DATA(lt_answers_text).

    IF sy-subrc EQ 0.
    ENDIF.

    LOOP AT lt_datos_eval_cir_subp ASSIGNING FIELD-SYMBOL(<fs_datos_eval_cir_subp>).
      CLEAR: ls_datos,
             ls_survey_template,
             lt_question_answer,
             lv_qsurvey_id,
             lo_object_qsurvey,
             lo_survey_response.

* Obtener preguntas y respuestas de la autoevaluación del riesgo.
      lv_qsurvey_id = cl_grfn_api_ident=>get_id_from_guid( i_entity = grfn0_c_entity-qsurvey
                                                           i_objid  = <fs_datos_eval_cir_subp>-svyinstid ).

      TRY.
          lo_object_qsurvey ?= go_session->get( lv_qsurvey_id ).

          IF lo_object_qsurvey IS BOUND.
            lo_survey_response = lo_object_qsurvey->get_survey_response_api( ).

            lo_survey_response->retrieve( EXPORTING iv_regulation_id   = gv_regulation_id " PREGUNTAR A DANI: Para que es esto exactamente gv_regulation_id.
                                          IMPORTING et_question_answer = lt_question_answer
                                                    es_survey          = ls_survey_template ).
          ENDIF.

        CATCH cx_grfn_exception.
          CONTINUE.
      ENDTRY.
    ENDLOOP.
  ENDIF.
---------
HOY
*&---------------------------------------------------------------------*
*& Include          ZBIGDATA_CIR_AUTO_SUBP_F01
*&---------------------------------------------------------------------*
*&---------------------------------------------------------------------*
*& Form SELECCION_CONSTRUCCION_DATOS
*&---------------------------------------------------------------------*
FORM seleccion_construccion_datos .
  CONSTANTS: lc_svy_type  TYPE string VALUE 'Z1',
             lc_i         TYPE string VALUE 'I',
             lc_eq        TYPE string VALUE 'EQ',
             lc_bt        TYPE string VALUE 'BT',
             lc_wi_type   TYPE string VALUE 'W',
             lc_completed TYPE string VALUE 'COMPLETED',
             lc_ready     TYPE string VALUE 'READY',
             lc_selected  TYPE string VALUE 'SELECTED',
             lc_cancelled TYPE string VALUE 'CANCELLED'.

  DATA: lr_instid          TYPE RANGE OF grfn_guid,
        lr_wi_rh_task      TYPE RANGE OF sww_task,
        lr_fecha           TYPE RANGE OF sy-datum,
        lv_nivel_ri        TYPE dd07l-domname,
        lt_dom_value       TYPE TABLE OF dd07v,
        lt_list            TYPE grfn_t_tf_tframe_list,
        lt_responsables    TYPE TABLE OF swhactor,
        lt_question_answer TYPE grfn_t_api_question_answer,
        lo_object_qsurvey  TYPE REF TO if_grfn_api_survey_resp_cont,
        lo_survey_response TYPE REF TO if_grfn_api_survey_response,
        ls_survey_template TYPE grpc_s_api_survey_data,
        ls_datos           TYPE gty_fichero,
        lv_qsurvey_id      TYPE grfn_api_object_id,
        lv_fecha           TYPE sy-datum.

  go_session = cl_grfn_api_session=>open_daily( ).

  " Obtencion de meses para el campo timeframe periodo.
  CALL METHOD cl_grfn_api_timeframe=>timeframes
    RECEIVING
      rt_list = lt_list.

  lr_wi_rh_task = VALUE #( sign   = lc_i
                           option = lc_eq
                         ( low    = 'TS90100016' )
                         ( low    = 'TS90100013' ) ).

* AUTOEVALUACIÖN:
  SELECT svyinst~svyinstid, " Id_autoevaluación
         svygroup~objectid, " Sproc_id
         svygroup~svygrpid, " ID grupo de la autoevaluación
         svyinst~completed_at, " Fecha completada de la autoevaluación
         taskplan~timeframe, " Periodo
         taskplan~tf_year,   " Año
         taskplangrp~taskplan_grp_nam, " Tipo_actividad
         svygroup~regulation, " Normativa
         taskplan~date_begin, " Fecha_lanzamiento
         taskplan~date_end,   " Fecha_vencimiento
         svyinst~scomment,    " Comentarios generales
         svyinst~zzcomentario, " Comentarios responsable
         grc_subp_sur~ries_inhv, " Riesgo inhernete cualitativo
         grc_subp_sur~amb_contv " Ambiente de control cualitativo
     INTO TABLE @DATA(lt_datos_eval_cir_subp)
     FROM grfntsvyinst AS svyinst
     INNER JOIN grfntsvygroup AS svygroup ON
                svygroup~svygrpid EQ svyinst~svygrpid
     INNER JOIN ztt_grc_subp_sur AS grc_subp_sur ON
                grc_subp_sur~survey_id EQ svyinst~svyinstid
     INNER JOIN grfntaskplan AS taskplan ON
                taskplan~taskplan_id EQ svygroup~taskplanid
     INNER JOIN grfntaskplangrp AS taskplangrp ON
                taskplangrp~taskplan_grp_id EQ taskplan~taskplan_grp_id
     WHERE svygroup~svy_type EQ @lc_svy_type.


  IF sy-subrc EQ 0.
    " Ordenamos las tareas de autoevaluacion por id de grupo y fecha completada,
    " quedando las completadas mas recientemente en primer lugar
    SORT lt_datos_eval_cir_subp BY svygrpid    DESCENDING
                                  completed_at DESCENDING.

    " Borramos los duplicados teniendo en cuenta el ID del grupo
    DELETE ADJACENT DUPLICATES FROM lt_datos_eval_cir_subp COMPARING svygrpid.

    " Rango para los instid
    lr_instid = VALUE #( FOR ls_datos_eval_cir_subp IN lt_datos_eval_cir_subp
                               sign   = lc_i
                               option = lc_eq
                             ( low    = ls_datos_eval_cir_subp-svyinstid ) ).

* DATOS TAREAS DEL WORKFLOW.
    SELECT
     wi2obj~instid,  " Id de la autoevaluación
     swwwihead~top_wi_id, " Id Workflow padre
     swwwihead~wi_id,   " Id workflow item
     swwwihead~wi_stat, " Estado del workflow
     swwwihead~wi_aed,   " Fecha fin
     swwwihead~wi_rh_task, " Tarea
     swwwihead~wi_aagent, " Responsable actual
     swwwihead~crea_tmp  "Para ordenar más reciente
    INTO TABLE @DATA(lt_tareas_wf)
    FROM swwwihead AS swwwihead
    INNER JOIN sww_wi2obj AS wi2obj ON
        wi2obj~top_wi_id EQ swwwihead~top_wi_id
    WHERE swwwihead~wi_type EQ @lc_wi_type AND
        swwwihead~wi_stat  NE @lc_cancelled AND
        wi2obj~instid IN @lr_instid AND
        swwwihead~wi_rh_task IN @lr_wi_rh_task
      ORDER BY swwwihead~top_wi_id, swwwihead~crea_tmp DESCENDING.

    IF sy-subrc EQ 0.
      DELETE ADJACENT DUPLICATES FROM lt_tareas_wf COMPARING top_wi_id.

      lr_instid = VALUE #( FOR ls_tarea_wf IN lt_tareas_wf
                               sign   = lc_i
                               option = lc_eq
                             ( low    = ls_tarea_wf-instid ) ).

      DELETE lt_datos_eval_cir_subp WHERE svyinstid NOT IN lr_instid.
    ENDIF.

* DATOS TEXTO DE LAS PREGUNTAS.
    SELECT *
      FROM grfnqlibchoicet
      INTO TABLE @DATA(lt_answers_text).

    IF sy-subrc EQ 0.
    ENDIF.

* DATOS PARA LOS UMBRALES DE LOS CAMPOS:
    " NIVEL RIESGO INHERENTE CUALITATIVO
    " NIVEL AMBIENTE DE CONTROL CUALITATIVO
    SELECT *
      FROM ztt_cir_result
      INTO TABLE @DATA(lt_cir_result)
      WHERE zz_objeto EQ 'OF'. " Para descartar los demás y solo centrarnos en los de subproceso.
    IF sy-subrc EQ 0.
      SORT lt_cir_result BY nivel ASCENDING.
    ENDIF.


    LOOP AT lt_datos_eval_cir_subp ASSIGNING FIELD-SYMBOL(<fs_datos_eval_cir_subp>).
      CLEAR: ls_datos,
             ls_survey_template,
             lt_question_answer,
             lv_qsurvey_id,
             lo_object_qsurvey,
             lo_survey_response.

* Obtener preguntas y respuestas de la autoevaluación del riesgo.
      lv_qsurvey_id = cl_grfn_api_ident=>get_id_from_guid( i_entity = grfn0_c_entity-qsurvey
                                                           i_objid  = <fs_datos_eval_cir_subp>-svyinstid ).

      TRY.
          lo_object_qsurvey ?= go_session->get( lv_qsurvey_id ).

          IF lo_object_qsurvey IS BOUND.
            lo_survey_response = lo_object_qsurvey->get_survey_response_api( ).

            lo_survey_response->retrieve( EXPORTING iv_regulation_id   = gv_regulation_id
                                          IMPORTING et_question_answer = lt_question_answer
                                                    es_survey          = ls_survey_template ).
          ENDIF.

        CATCH cx_grfn_exception.
          CONTINUE.
      ENDTRY.

* Rellenar datos de la tarea de autoevaluación
      ls_datos-id_autoevaluacion       = <fs_datos_eval_cir_subp>-svyinstid.
      ls_datos-sproc_id                = <fs_datos_eval_cir_subp>-objectid.
      ls_datos-anyo                    = <fs_datos_eval_cir_subp>-tf_year.
      ls_datos-tipo_actividad          = <fs_datos_eval_cir_subp>-taskplan_grp_nam.
      ls_datos-normativa               = <fs_datos_eval_cir_subp>-regulation.
      ls_datos-fecha_inicio            = <fs_datos_eval_cir_subp>-date_begin.
      ls_datos-fecha_vencimiento       = <fs_datos_eval_cir_subp>-date_end.
      ls_datos-comentarios_generales   = <fs_datos_eval_cir_subp>-scomment.
      ls_datos-comentarios_responsable = <fs_datos_eval_cir_subp>-zzcomentario.

      " Le quito espacios en blanco.
      ls_datos-ri_cualitativo_encuesta = <fs_datos_eval_cir_subp>-ries_inhv.
      CONDENSE ls_datos-ri_cualitativo_encuesta NO-GAPS.
      ls_datos-ac_cualitativo_encuesta = <fs_datos_eval_cir_subp>-amb_contv.
      CONDENSE ls_datos-ac_cualitativo_encuesta NO-GAPS.

      READ TABLE lt_list INTO DATA(ls_periodo) WITH KEY timeframe = <fs_datos_eval_cir_subp>-timeframe.
      IF sy-subrc EQ 0.
        ls_datos-periodo = ls_periodo-text.
      ENDIF.

* Rellenamos los campos nivel riesgo inherente cualitativo
*  y nivel ambiente de control cualitativo
      LOOP AT lt_cir_result ASSIGNING FIELD-SYMBOL(<fs_cir_result>) WHERE
                                                           ( valor_umbral_minimo LE ls_datos-ri_cualitativo_encuesta AND
                                                           valor_umbral_maximo GE ls_datos-ri_cualitativo_encuesta ) OR
                                                           ( valor_umbral_minimo LE ls_datos-ac_cualitativo_encuesta AND
                                                           valor_umbral_maximo GE ls_datos-ac_cualitativo_encuesta ).
        lv_nivel_ri = <fs_cir_result>-nivel.

      ENDLOOP.

* Sacamos el nombre del texto a partir del dominio del elemento de datos con la funcion DOM_VALUES_GET.
      CALL FUNCTION 'DD_DOMVALUES_GET'
        EXPORTING
          domname   = 'ZDM_NIV_RINH'
          text      = 'X'
          langu     = sy-langu
        TABLES
          dd07v_tab = lt_dom_value.

* Leemos la tabla resultante con los niveles, cogemos el texto y rellenamos en el fichero.
      READ TABLE lt_dom_value ASSIGNING FIELD-SYMBOL(<fs_dom_value>) WITH KEY domvalue_l = <fs_cir_result>-nivel.
      IF sy-subrc EQ 0.
        ls_datos-nivel_ri_cualitativo_encuesta = <fs_dom_value>-ddtext.
        ls_datos-nivel_ac_cualitativo_encuesta = <fs_dom_value>-ddtext.
      ENDIF.

* Rellenar datos del Workflow de la tarea de autoevaluación de riesgo.
      READ TABLE lt_tareas_wf ASSIGNING FIELD-SYMBOL(<fs_tarea_wf>) WITH KEY instid = <fs_datos_eval_cir_subp>-svyinstid.
      IF sy-subrc EQ 0.
        " Fecha Fin (Cierre del Workflow)
        IF <fs_tarea_wf>-wi_stat NE lc_completed.
          CLEAR ls_datos-fecha_fin.
        ELSE.
          ls_datos-fecha_fin = <fs_tarea_wf>-wi_aed.
        ENDIF.

        " Estado de la tarea de autoevaluación (workflow)
        ls_datos-estado = COND #( WHEN <fs_tarea_wf>-wi_stat EQ lc_ready     THEN 'Enviado'
                                  WHEN <fs_tarea_wf>-wi_stat EQ lc_selected  THEN 'En tratamiento'
                                  WHEN <fs_tarea_wf>-wi_stat EQ lc_completed THEN 'Finalizado' ).

        " Responsable de la tarea de autoevaluación
        IF <fs_tarea_wf>-wi_aagent IS INITIAL.

          CALL FUNCTION 'SWW_WI_AGENTS_READ'
            EXPORTING
              wi_id  = <fs_tarea_wf>-wi_id
            TABLES
              agents = lt_responsables.

          READ TABLE lt_responsables INDEX 1 INTO DATA(ls_responsable).
          ls_datos-responsable_actual = ls_responsable-objid.

        ELSE.
          ls_datos-responsable_actual = <fs_tarea_wf>-wi_aagent.
        ENDIF.

* Rellenar datos de la pregunta y respuesta, por cada línea
        LOOP AT lt_question_answer ASSIGNING FIELD-SYMBOL(<fs_question_answer>).

          CLEAR: gs_datos_fichero.

          MOVE-CORRESPONDING ls_datos TO gs_datos_fichero.

          gs_datos_fichero-pregunta            = <fs_question_answer>-text. " Texto de la pregunta
          gs_datos_fichero-comentario_pregunta = <fs_question_answer>-comments. " Comentario de la pregunta

          READ TABLE lt_answers_text INTO DATA(ls_answer_text) WITH KEY langu       = sy-langu
                                                                        question_id = cl_grfn_api_ident=>get_guid( <fs_question_answer>-question_id )
                                                                        cust_choice = <fs_question_answer>-cust_choice.
          IF sy-subrc EQ 0.
            gs_datos_fichero-respuesta = ls_answer_text-text.
          ENDIF.

          APPEND gs_datos_fichero TO gt_datos_fichero.

        ENDLOOP.
      ELSE.
        CONTINUE.
      ENDIF.
    ENDLOOP.

* si el check 'Delta Diario' si esta marcado, debe enviar las autoevaluaciones abiertas y las cerradas dentro de la fecha informada/actual
* Si el check 'Delta Diario' NO esta marcado, debe enviar las autoevaluaciones abiertas y cerradas de todos los tiempos
    IF gt_datos_fichero IS NOT INITIAL AND
       p_check EQ abap_true.

      IF s_fecha[] IS NOT INITIAL. " Si el rango de fechas está informado

        IF s_fecha-low IS NOT INITIAL AND
           s_fecha-high IS NOT INITIAL.
          lr_fecha  = VALUE #( sign   = lc_i
                               option = lc_bt
                             ( low    = s_fecha-low
                               high   = s_fecha-high ) ).

          " Mantener cerradas que esten en el rango de fechas
          DELETE gt_datos_fichero WHERE estado EQ 'Finalizado' AND fecha_fin NOT IN lr_fecha.

        ELSE. " Si uno de los campos fecha esta informado
          lv_fecha = COND #( WHEN s_fecha-low IS NOT INITIAL THEN s_fecha-low
                             WHEN s_fecha-high IS NOT INITIAL THEN s_fecha-high ).

          DELETE gt_datos_fichero WHERE estado EQ 'Finalizado' AND fecha_fin NE lv_fecha.
        ENDIF.

      ELSE. " Si no hay rango de fecha informado, utilizamos la fecha actual
        lv_fecha = sy-datum - 1.

        DELETE gt_datos_fichero WHERE estado EQ 'Finalizado' AND fecha_fin NE lv_fecha.
      ENDIF.

    ENDIF.
  ENDIF.
ENDFORM.
*&---------------------------------------------------------------------*
*& Form GENERACION_FICHERO
*&---------------------------------------------------------------------*
FORM generacion_fichero.

  CONSTANTS: lc_nombre_fich TYPE string VALUE 'MRC00240'.

  DATA: ls_file_write TYPE gty_fichero,
        lv_file       TYPE string,
        lv_ruta       TYPE string,
        lv_txt        TYPE string,
        lv_length     TYPE i,
        lv_info       TYPE string,
        lv_error      TYPE string,
        lo_table_desc TYPE REF TO cl_abap_tabledescr,
        lo_descr_ref  TYPE REF TO cl_abap_structdescr.

  FIELD-SYMBOLS: <lfs_field> TYPE any.

  DESCRIBE FIELD ls_file_write LENGTH lv_length IN CHARACTER MODE.

  " Obtener ruta y extensión del fichero
  PERFORM constantes CHANGING lv_ruta lv_txt.

  " Si el nombre del fichero se ha introducido en la pantalla, se recoge de ahí
  IF p_fich IS NOT INITIAL.
    CONCATENATE lv_ruta p_fich sy-datum lv_txt INTO lv_file.
  ELSE.
    " Si no le añadimos el nombre del fichero por defecto y la fecha.
    CONCATENATE lv_ruta lc_nombre_fich sy-datum lv_txt INTO lv_file.
  ENDIF.

  " Abrimos el fichero para escritura
  OPEN DATASET lv_file FOR OUTPUT IN LEGACY TEXT MODE CODE PAGE '1160'.

  LOOP AT gt_datos_fichero INTO DATA(ls_fichero).
    MOVE-CORRESPONDING ls_fichero TO ls_file_write.

    " Obtenemos el objeto del fichero.
    lo_table_desc ?= cl_abap_typedescr=>describe_by_data( gt_datos_fichero ).

    " Obtenemos el objetos de cada campo.
    lo_descr_ref ?= lo_table_desc->get_table_line_type( ).

    " Recorremos los componentes del fichero para eliminar tildes, y añadirle espacios.
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
                 ALL OCCURRENCES OF 'Ú' IN <lfs_field> WITH 'U',
                 ALL OCCURRENCES OF cl_abap_char_utilities=>cr_lf IN <lfs_field> WITH space,
                 ALL OCCURRENCES OF cl_abap_char_utilities=>newline IN <lfs_field> WITH space,
                 ALL OCCURRENCES OF cl_abap_char_utilities=>horizontal_tab IN <lfs_field> WITH space.
      ENDIF.

    ENDLOOP.
    TRY.
* PARA DANI: El fichero que me crea es mas grande que el que muestra en la al11.
* En los campos cualitativo tiene espacios en blanco.
        " Escribimos las línea en el fichero
        TRANSFER ls_file_write TO lv_file LENGTH lv_length.
        CLEAR: ls_file_write.
      CATCH cx_sy_conversion_codepage.
        WRITE: 'Error en conversion:', ls_file_write-id_autoevaluacion.
    ENDTRY.
  ENDLOOP.

  lv_info = 'Fichero exportado: &1 Longitud de línea: '.
  REPLACE '&1' WITH lv_file INTO lv_info.
  WRITE: lv_info, lv_length.

  CLOSE DATASET lv_file.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form CONSTANTES
*&---------------------------------------------------------------------*
FORM constantes  CHANGING lv_ruta TYPE string lv_txt TYPE string.
  DATA: lt_const TYPE gtt_const,
        ls_const TYPE gty_const.

  SELECT tipo low
    FROM ztt_grc_constant
    INTO TABLE lt_const
    WHERE id_prog EQ 'ZBIGDATA_GRC'.

  CLEAR: ls_const.
  READ TABLE lt_const INTO ls_const WITH KEY tipo = 'RUTA'.
  lv_ruta = ls_const-low.

  CLEAR: ls_const.
  READ TABLE lt_const INTO ls_const WITH KEY tipo = 'EXTENSION'.
  lv_txt = ls_const-low.
ENDFORM.

---
INCIDENCIA
METHOD onactionir.

  TYPES: BEGIN OF typ_resp,
           id_control TYPE hrobjid,
           resp       TYPE grfn_text,
         END OF typ_resp.

  TYPES: BEGIN OF typ_data.
           INCLUDE TYPE zst_cir_informe_kci_cir.
           TYPES: subprocess_id  TYPE hrobjid,
           subprocess_txt TYPE grfn_title,
           "control_id     TYPE hrobjid,
           control_txt    TYPE grfn_title,

         END OF typ_data,

         typ_t_data TYPE TABLE OF typ_data.

  DATA(lo_amdp) = NEW zcl_amdp_informes_cir( ).

  DATA: lt_alv_kci TYPE STANDARD TABLE OF zst_cir_informe_kci_cir,
        ls_alv_kci TYPE zst_cir_informe_kci_cir.

  DATA(lo_help_general) = wd_this->wd_cpifc_help_general( ).
  DATA: lv_aux      TYPE hrobjid,
        lt_data     TYPE typ_t_data,
        lt_data_aux TYPE typ_t_data,
        lt_informe  TYPE STANDARD TABLE OF zst_cir_informe_kci_cir,
        lv_descr    TYPE grfn_text,
        lt_resp     TYPE STANDARD TABLE OF typ_resp.

  DATA: lv_date          TYPE sy-datum,
        lv_last_day      TYPE sy-datum,
        lv_first_day     TYPE sy-datum,
        lv_date_ant      TYPE sy-datum,
        lv_last_day_ant  TYPE sy-datum,
        lv_first_day_ant TYPE sy-datum,
        lv_month         TYPE /osp/dt_rp_month,
        lr_subprc_id     TYPE RANGE OF hrobjid,
        lr_contr_id      TYPE RANGE OF hrobjid,
        lr_kci           TYPE RANGE OF hrp1000-objid,
        lr_control       TYPE RANGE OF hrp1000-objid,
        lr_risk_id       TYPE RANGE OF hrobjid.

*INI WCMG 02.08.2024 CIR - OPTIMIZACION DE INFORMES
  lo_help_general->recuperar_datos( ).
*INI WCMG 02.08.2024 CIR - OPTIMIZACION DE INFORMES

*  " Primero, recuperamos todos los dominios
*  DATA(lt_domvalue_nivel_riesgo)    = VALUE dd07v_tab( ).
*  DATA(lt_domvalue_rres)            = VALUE dd07v_tab( ).
*  DATA(lt_domvalue_nvl_ambiente)    = VALUE dd07v_tab( ).

  DATA(lo_el_context) = wd_context->get_element( ).
  lo_el_context->set_attribute(
    name =  `ENABLED`
    value = abap_false ).

  " Primero, recuperamos todos los dominios
  DATA(lt_domvalue_nivel_riesgo)    = VALUE dd07v_tab( ).
  DATA(lt_domvalue_rres)            = VALUE dd07v_tab( ).
  DATA(lt_dom_status)               = VALUE dd07v_tab( ).
  DATA(lt_clas_indi)                = VALUE dd07v_tab( ).
  DATA(lt_dim_indi)                 = VALUE dd07v_tab( ).
  DATA(lt_tipo_umbral)              = VALUE dd07v_tab( ).
  DATA(lt_tend_indic)               = VALUE dd07v_tab( ).
  DATA(lt_result_eva)               = VALUE dd07v_tab( ).
  DATA(lt_riesgo_inh)               = VALUE dd07v_tab( ).
  DATA(lt_dom_fecuencia)            = VALUE dd07v_tab( ).
  DATA(lt_valor_ambiente)           = VALUE dd07v_tab( ).
* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
  DATA(lt_publicado)                = VALUE dd07v_tab( ).
  DATA(lt_visible_ci)               = VALUE dd07v_tab( ).
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024


  " Recuperamos el dominio del status
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'GRRM_KRI_INST_STATUS'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_dom_status
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio del status
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_PERIODICIDAD'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_dom_fecuencia
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de clase indicador
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_CLASE_INDICADOR'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_clas_indi
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de dimension indicador
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_DIMENSION_INDICADOR'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_dim_indi
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de tipo umbral
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_TIPO_UMBRAL'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_tipo_umbral
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de tendencia indicador
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_TENDENCIA_INDICADOR_N'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_tend_indic
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de resultado evaluación
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_RESUL_EVA_NUM'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_result_eva
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de riesgo inherente
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDE_NIVEL'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_riesgo_inh
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de riesgo inherente
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_NIVEL_AMBIENTE_CONTROL'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_valor_ambiente
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.
* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
  " Recuperamos el dominio de publicado
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_PUBLICADO'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_publicado
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.


  " Recuperamos el dominio de visible cir
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDE_VISIBLE_CIR'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_visible_ci
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024

* Recuperamos los filtros de la pantalla de selección
  lo_help_general->recuperar_filtros(
    IMPORTING
      et_control             = DATA(lt_control)
      et_process             = DATA(lt_process)
      et_process_lvl_2       = DATA(lt_process_lvl_2)
      et_process_lvl_3       = DATA(lt_process_lvl_3)
      et_process_lvl_4       = DATA(lt_process_lvl_4)
      et_riesgos             = DATA(lt_riesgos)
      et_subprocess          = DATA(lt_subprocess)
      et_subproc_by_lvl_proc = DATA(lt_subproc_by_lvl_proc)
      et_kci                 = DATA(lt_kci)
      ev_control_id          = DATA(lv_control_id)
      ev_proc_id_lvl_1       = DATA(lv_proc_id_lvl_1)
      ev_proc_id_lvl_2       = DATA(lv_proc_id_lvl_2)
      ev_proc_id_lvl_3       = DATA(lv_proc_id_lvl_3)
      ev_proc_id_lvl_4       = DATA(lv_proc_id_lvl_4)
      ev_risk_id             = DATA(lv_risk_id)
      ev_subproc_id          = DATA(lv_subproc_id)
      ev_kci_id              = DATA(lv_kci_id)
      ev_anyo                = DATA(lv_anyo)
      es_periodo             = DATA(ls_periodo)
      ev_anyo_ant            = DATA(lv_anyo_ant)
      es_periodo_ant         = DATA(ls_periodo_ant)
      ) .

  "Eliminamos aquellas líneas que no tengan Subproceso, ya que no tendrán Controles asignados
  DELETE lt_subproc_by_lvl_proc WHERE subprocess_id IS INITIAL.

  IF lv_kci_id IS NOT INITIAL.

    lr_kci   = VALUE #( sign   = 'I'
                       option = 'EQ'
                     (  low    = lv_kci_id ) ) .

  ENDIF.

  IF lv_control_id IS NOT INITIAL.

    lr_control   = VALUE #( sign   = 'I'
                       option = 'EQ'
                     (  low    = lv_control_id ) ) .

  ENDIF.

  IF ls_periodo-id_periodo CS '0SAPM_'.

    lv_month = ls_periodo-id_periodo+6(2).

    lv_date      = lv_anyo && lv_month && '01'.
    lv_first_day = lv_anyo && lv_month && '01'.

  ELSEIF ls_periodo-id_periodo EQ '0SAPY_YEAR'.

    lv_date      = lv_anyo && '1201'.
    lv_first_day = lv_anyo && '0101'.

  ENDIF.

  CALL FUNCTION 'SN_LAST_DAY_OF_MONTH'
    EXPORTING
      day_in       = lv_date
    IMPORTING
      end_of_month = lv_last_day.

  IF ls_periodo_ant-id_periodo CS '0SAPM_'.

    lv_month = ls_periodo_ant-id_periodo+6(2).

    lv_date_ant      = lv_anyo_ant && lv_month && '01'.
    lv_first_day_ant = lv_anyo_ant && lv_month && '01'.

  ELSEIF ls_periodo_ant-id_periodo EQ '0SAPY_YEAR'.

    lv_date_ant      = lv_anyo_ant && '1201'.
    lv_first_day_ant = lv_anyo_ant && '0101'.

  ENDIF.

  CALL FUNCTION 'SN_LAST_DAY_OF_MONTH'
    EXPORTING
      day_in       = lv_date_ant
    IMPORTING
      end_of_month = lv_last_day_ant.

*ZST_CIR_INFORME_KCI_CIR
  DATA lr_kci_id TYPE RANGE OF hrobjid.

  IF lv_proc_id_lvl_4 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING FIELD-SYMBOL(<ls_subproc_by_lvl_proc>)
          WHERE process1_id EQ lv_proc_id_lvl_1
            AND process2_id EQ lv_proc_id_lvl_2
            AND process3_id EQ lv_proc_id_lvl_3
            AND process4_id EQ lv_proc_id_lvl_4.
      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO DATA(ls_aux) WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.

            APPEND INITIAL LINE TO lt_data ASSIGNING FIELD-SYMBOL(<lfs_data>).
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zdesc_indi     = ls_aux-descr.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.


          ENDLOOP.

          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.

          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

    " Se informan 3 niveles de procesos
  ELSEIF lv_proc_id_lvl_3 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
          WHERE process1_id EQ lv_proc_id_lvl_1
            AND process2_id EQ lv_proc_id_lvl_2
            AND process3_id EQ lv_proc_id_lvl_3.
      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


            APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.




          ENDLOOP.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

    " Se informan 2 niveles de procesos
  ELSEIF lv_proc_id_lvl_2 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
          WHERE process1_id EQ lv_proc_id_lvl_1
            AND process2_id EQ lv_proc_id_lvl_2.
      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


            APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.


          ENDLOOP.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

    " Se informa solo el proceso de nivel 1
  ELSEIF lv_proc_id_lvl_1 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
          WHERE process1_id EQ lv_proc_id_lvl_1.

      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.

            APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.



          ENDLOOP.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.

          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

  ELSEIF lv_subproc_id IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
        WHERE subprocess_id EQ lv_subproc_id.

      " Buscamos si tiene control asociado
      IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

        LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-control_id.
          <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-descr.



        ENDLOOP.


        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


      ELSE.

        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


      ENDIF.

    ENDLOOP.

  ELSE.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>.

      " Buscamos si tiene control asociado
      IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

        LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-control_id.
          <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-descr.

        ENDLOOP.

        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


      ELSE.

        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.

      ENDIF.

    ENDLOOP.

  ENDIF.


  CALL METHOD lo_amdp->get_kci_cir
    EXPORTING
      im_client     = sy-mandt
      it_kci        = lt_kci
      im_period     = lv_last_day
      im_period_old = lv_last_day_ant
    IMPORTING
      im_kci        = DATA(lt_kci_pro).

  IF lt_kci_pro IS NOT INITIAL.

    SORT lt_kci_pro BY kci_id.

    DATA(lt_kci_pro_eval) = lt_kci_pro[].
    DATA(lt_kci_pro_resp) = lt_kci_pro[].

*        DATA lv_desc TYPE string.
    DATA lv_desc_final TYPE string.
    TYPES: BEGIN OF ltys_desc,
             kci_id TYPE hrp1002-objid,
           END OF ltys_desc.
    DATA lt_kci_aux    TYPE STANDARD TABLE OF ltys_desc.

    lt_kci_aux = CORRESPONDING #( lt_kci ).
*INI DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
*    SELECT  a~objid, b~tabseqnr, b~tline
    SELECT  a~objid, b~tabseqnr, a~begda, a~endda, b~tline, a~tabnr
*FIN DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
     FROM hrp1002 AS a
     INNER JOIN hrt1002 AS b ON a~tabnr EQ b~tabnr
      FOR ALL ENTRIES IN @lt_kci_aux
     WHERE a~objid EQ @lt_kci_aux-kci_id
     AND a~otype EQ 'Z5'
      INTO TABLE @DATA(lt_desc).
*INI DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
*    SORT lt_desc BY objid ASCENDING tabseqnr ASCENDING.
    SORT lt_desc BY objid ASCENDING tabseqnr ASCENDING begda DESCENDING endda DESCENDING.

*    DELETE ADJACENT DUPLICATES FROM lt_kci_pro COMPARING kci_id.
    DELETE ADJACENT DUPLICATES FROM lt_desc COMPARING objid tabseqnr.
*FIN DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
    " Sacamos los responsables
    SORT lt_kci_pro_resp BY zcontrol_rel zresp_control.
    DELETE ADJACENT DUPLICATES FROM lt_kci_pro_resp COMPARING zcontrol_rel zresp_control.

    LOOP AT lt_kci_pro_resp INTO DATA(ls_kci_pro_resp).

      IF NOT line_exists( lt_resp[ id_control = ls_kci_pro_resp-zcontrol_rel ] ).

        APPEND INITIAL LINE TO lt_resp ASSIGNING FIELD-SYMBOL(<lfs_resp>).
        <lfs_resp>-id_control = ls_kci_pro_resp-zcontrol_rel.
        <lfs_resp>-resp = REDUCE #( INIT lv_resp TYPE grfn_text
                          FOR  ls_control_aux IN lt_kci_pro_resp
                          WHERE ( zcontrol_rel = ls_kci_pro_resp-zcontrol_rel )
                          NEXT lv_resp = COND #( WHEN lv_resp IS INITIAL
                                                 THEN ls_control_aux-zresp_control
                                                 ELSE lv_resp && ',' && ls_control_aux-zresp_control ) ).

      ENDIF.

    ENDLOOP.

    LOOP AT lt_kci INTO DATA(ls_kci).

      ls_alv_kci-zid_kci = ls_kci-kci_id.
      ls_alv_kci-zid_risk = ls_kci-control_id.

      DATA lv_numero TYPE p LENGTH 16 DECIMALS 2.

      READ TABLE lt_kci_pro ASSIGNING FIELD-SYMBOL(<fs_kci_pro>) WITH KEY kci_id = ls_kci-kci_id.
      IF sy-subrc EQ 0.
        MOVE-CORRESPONDING <fs_kci_pro> TO ls_alv_kci.

        lv_numero = <fs_kci_pro>-zvalor_num_eur.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_num_n.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_n CURRENCY 'EUR'.

        MOVE <fs_kci_pro>-zumb_min_n TO lv_numero.
        WRITE lv_numero TO ls_alv_kci-zumb_min_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zumb_max_n.
        WRITE lv_numero TO ls_alv_kci-zumb_max_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zumb_min_eur.
        WRITE lv_numero TO ls_alv_kci-zumb_min_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zumb_max_eur.
        WRITE lv_numero TO ls_alv_kci-zumb_max_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_n.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_eur.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_n.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_eur.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_num_eur_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_eur_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_eur_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_eur_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_eur_ant.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_eur_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_n_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_n_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_num_n_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_n_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_n_ant.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_n_ant CURRENCY 'EUR'.

      ENDIF.

      READ TABLE lt_data INTO DATA(ls_data) WITH KEY zcontrol_rel = <fs_kci_pro>-zcontrol_rel.
      IF sy-subrc EQ 0.

        ls_alv_kci-zproc_n1_id      = ls_data-zproc_n1_id.
        ls_alv_kci-zproc_n1_txt     = ls_data-zproc_n1_txt.
        ls_alv_kci-zproc_n2_id      = ls_data-zproc_n2_id.
        ls_alv_kci-zproc_n2_txt     = ls_data-zproc_n2_txt.
        ls_alv_kci-zproc_n3_id      = ls_data-zproc_n3_id.
        ls_alv_kci-zproc_n3_txt     = ls_data-zproc_n3_txt.
        ls_alv_kci-zproc_n4_id      = ls_data-zproc_n4_id.
        ls_alv_kci-zproc_n4_txt     = ls_data-zproc_n4_txt.
        ls_alv_kci-zsubproc_id      = ls_data-zsubproc_id.
        ls_alv_kci-zsubproc_txt     = ls_data-zsubproc_txt.
        ls_alv_kci-zyear_act        = lv_anyo.
        ls_alv_kci-zperiod_act      = ls_periodo-periodo.
        ls_alv_kci-zyear_ant        = lv_anyo_ant.
        ls_alv_kci-zperiod_ant      = ls_periodo_ant-periodo.
*        ls_alv_kci-zamb_control     = <fs_kci_pro>-zamb_control.
*        ls_alv_kci-zamb_control_ant = <fs_kci_pro>-zamb_control_ant.

        ls_alv_kci-zdesc_indi   = REDUCE #( INIT lv_desc TYPE string
                          FOR  ls_desc IN lt_desc
                          WHERE ( objid = ls_kci-kci_id )
                          NEXT lv_desc = COND #( WHEN lv_desc IS INITIAL
                                                 THEN ls_desc-tline
                                                 ELSE lv_desc && ' ' && ls_desc-tline ) ).

        ls_alv_kci-zdesc_indi = replace( val   = ls_alv_kci-zdesc_indi
                                         regex = cl_abap_char_utilities=>horizontal_tab
                                         with  = ''
                                         occ   = 0 ).

        ls_alv_kci-znom_indi    = <fs_kci_pro>-znom_indi.
*        ls_alv_kci-zid_kci      = <fs_kci_pro>-kci_id.

        ls_alv_kci-zestado            = VALUE #( lt_dom_status[ domvalue_l = <fs_kci_pro>-zestado            " Estado
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
        ls_alv_kci-zpublicado           = VALUE #( lt_publicado[ domvalue_l = <fs_kci_pro>-zpublicado         " Publicado
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).
        IF  <fs_kci_pro>-zvisible_ci IS NOT INITIAL.
          ls_alv_kci-zvisible_ci         = 'Si'.        " Visible CI
        ELSE.
          ls_alv_kci-zvisible_ci         = 'No' .        " Visible CI
        ENDIF.


* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024

        ls_alv_kci-zclase_indi        = VALUE #( lt_clas_indi[ domvalue_l = <fs_kci_pro>-zclase_indi         " Clase Indicador
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zdimen_indi        = VALUE #( lt_dim_indi[ domvalue_l = <fs_kci_pro>-zdimen_indi          " Dimension Indicador
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).
        IF <fs_kci_pro>-zdimen_indi EQ 01.
          " EUROS
          CLEAR:
          <fs_kci_pro>-zvalor_num_eur,
          <fs_kci_pro>-zvalor_den_eur,
          <fs_kci_pro>-zresul_indi_eur,
          <fs_kci_pro>-ztend_ind_eur,
          <fs_kci_pro>-zresul_eva_eur,
          <fs_kci_pro>-zumb_min_eur,
          <fs_kci_pro>-zumb_max_eur,
          <fs_kci_pro>-zvalor_num_eur_ant,
          <fs_kci_pro>-zvalor_den_eur_ant,
          <fs_kci_pro>-zresul_indi_eur_ant,

          ls_alv_kci-zvalor_num_eur,
          ls_alv_kci-zvalor_den_eur,
          ls_alv_kci-zresul_indi_eur,
          ls_alv_kci-ztend_ind_eur,
          ls_alv_kci-zumb_min_eur,
          ls_alv_kci-zumb_max_eur,
          ls_alv_kci-zresul_eva_eur,
          ls_alv_kci-zvalor_num_eur_ant,
          ls_alv_kci-zresul_indi_eur_ant,
          ls_alv_kci-zvalor_den_eur_ant.

        ELSEIF <fs_kci_pro>-zdimen_indi EQ 02.
          " NUMEROS
          CLEAR:
          <fs_kci_pro>-zresul_eva_n,
          <fs_kci_pro>-zvalor_num_n,
          <fs_kci_pro>-zvalor_den_n,
          <fs_kci_pro>-zresul_indi_n,
          <fs_kci_pro>-ztend_ind_n,
          <fs_kci_pro>-zumb_min_n,
          <fs_kci_pro>-zumb_max_n,
          <fs_kci_pro>-zvalor_den_n_ant,
          <fs_kci_pro>-zvalor_num_n_ant,
          <fs_kci_pro>-zresul_indi_n_ant,

          ls_alv_kci-zvalor_num_n,
          ls_alv_kci-zvalor_den_n,
          ls_alv_kci-zresul_indi_n,
          ls_alv_kci-ztend_ind_n,
          ls_alv_kci-zumb_min_n,
          ls_alv_kci-ztend_ind_n,
          ls_alv_kci-zumb_max_n,
          ls_alv_kci-zvalor_den_n_ant,
          ls_alv_kci-zvalor_num_n_ant,
          ls_alv_kci-zresul_indi_n_ant.

        ENDIF.

        ls_alv_kci-ztipo_umbral       = VALUE #( lt_tipo_umbral[ domvalue_l = <fs_kci_pro>-ztipo_umbral      " Tipo Umbral
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_n        = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_n        " Tendencia indicador n
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_eur      = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_eur      " Tendencia indicador eur
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_n_ant    = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_n_ant    " Tendencia indicador n anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_eur_ant  = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_eur_ant  " Tendencia indicador eur anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_n       = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_n       " Resultado evaluación N
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_eur     = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_eur     " Resultado evaluación EUR
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_n_ant   = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_n_ant   " Resultado evaluación N anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_eur_ant = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_eur_ant " Resultado evaluación EUR anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zamb_control       = VALUE #( lt_valor_ambiente[ domvalue_l = <fs_kci_pro>-zamb_control     " Ambiente de control
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
        ls_alv_kci-zres_amb_control     = <fs_kci_pro>-zres_amb_control.   " Resultado Ambiente de control
        ls_alv_kci-zval_amb_control     = <fs_kci_pro>-zval_amb_control.   " Valor Ambiente de control
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024

        ls_alv_kci-zamb_control_ant   = VALUE #( lt_valor_ambiente[ domvalue_l = <fs_kci_pro>-zamb_control_ant " Ambiente de control anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
        ls_alv_kci-zres_amb_control_ant     = <fs_kci_pro>-zres_amb_control_ant.   " Resultado Ambiente de control anterior
        ls_alv_kci-zval_amb_control_ant     = <fs_kci_pro>-zval_amb_control_ant.   " Valor Ambiente de control anterior
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024


        ls_alv_kci-zfrec_medida       = VALUE #( lt_dom_fecuencia[ domvalue_l = <fs_kci_pro>-zfrec_medida    " Frecuencia medida
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI JAGM 25.04.2023 - Incidencia Visibilidad TODOS los KCIs/KRIs(solo debe ver los suyos)
      ELSE.
        CONTINUE.
* FIN JAGM 25.04.2023 - Incidencia Visibilidad TODOS los KCIs/KRIs(solo debe ver los suyos)

      ENDIF.

      READ TABLE lt_resp INTO DATA(ls_resp) WITH KEY id_control = <fs_kci_pro>-zcontrol_rel.
      IF sy-subrc EQ 0.
        DATA lv_control_rel TYPE string.

        ls_alv_kci-zresp_control = ls_resp-resp.

        SELECT SINGLE stext
          FROM hrp1000
          INTO lv_control_rel
          WHERE objid = <fs_kci_pro>-zcontrol_rel
          AND otype = 'P2'.

        ls_alv_kci-zcontrol_rel = lv_control_rel.

        CLEAR lv_control_rel.


      ENDIF.
      APPEND ls_alv_kci TO lt_alv_kci.
      CLEAR ls_alv_kci.
    ENDLOOP.

    IF lr_kci IS NOT INITIAL.

      DELETE lt_alv_kci WHERE zid_kci NOT IN lr_kci.

    ENDIF.

    IF lr_control IS NOT INITIAL.

      DELETE lt_alv_kci WHERE zid_risk NOT IN lr_control.

    ENDIF.



    SORT lt_alv_kci BY     zproc_n1_id    ASCENDING
                           zproc_n2_id    ASCENDING
                           zproc_n3_id    ASCENDING
                           zproc_n4_id    ASCENDING.

    DATA(lt_data_informe) = VALUE wd_comp_controller->elements_data( ).
    DATA(lo_data_informe) = wd_context->get_child_node( wd_this->wdctx_data ).

    lt_data_informe = CORRESPONDING #( lt_alv_kci ).

    lo_data_informe->invalidate( ).

    IF lt_data_informe IS NOT INITIAL.

      lo_data_informe->bind_table( EXPORTING new_items = lt_data_informe ).

    ENDIF.

  ENDIF.

ENDMETHOD.

-----
TYPES: BEGIN OF typ_resp,
           id_control TYPE hrobjid,
           resp       TYPE grfn_text,
         END OF typ_resp.

  TYPES: BEGIN OF typ_data.
           INCLUDE TYPE zst_cir_informe_kci_cir.
           TYPES: subprocess_id  TYPE hrobjid,
           subprocess_txt TYPE grfn_title,
           "control_id     TYPE hrobjid,
           control_txt    TYPE grfn_title,

         END OF typ_data,

         typ_t_data TYPE TABLE OF typ_data.

  DATA(lo_amdp) = NEW zcl_amdp_informes_cir( ).

  DATA: lt_alv_kci TYPE STANDARD TABLE OF zst_cir_informe_kci_cir,
        ls_alv_kci TYPE zst_cir_informe_kci_cir.

  DATA(lo_help_general) = wd_this->wd_cpifc_help_general( ).
  DATA: lv_aux      TYPE hrobjid,
        lt_data     TYPE typ_t_data,
        lt_data_aux TYPE typ_t_data,
        lt_informe  TYPE STANDARD TABLE OF zst_cir_informe_kci_cir,
        lv_descr    TYPE grfn_text,
        lt_resp     TYPE STANDARD TABLE OF typ_resp.

  DATA: lv_date          TYPE sy-datum,
        lv_last_day      TYPE sy-datum,
        lv_first_day     TYPE sy-datum,
        lv_date_ant      TYPE sy-datum,
        lv_last_day_ant  TYPE sy-datum,
        lv_first_day_ant TYPE sy-datum,
        lv_month         TYPE /osp/dt_rp_month,
        lr_subprc_id     TYPE RANGE OF hrobjid,
        lr_contr_id      TYPE RANGE OF hrobjid,
        lr_kci           TYPE RANGE OF hrp1000-objid,
        lr_control       TYPE RANGE OF hrp1000-objid,
        lr_risk_id       TYPE RANGE OF hrobjid.

*INI WCMG 02.08.2024 CIR - OPTIMIZACION DE INFORMES
  lo_help_general->recuperar_datos( ).
*INI WCMG 02.08.2024 CIR - OPTIMIZACION DE INFORMES

*  " Primero, recuperamos todos los dominios
*  DATA(lt_domvalue_nivel_riesgo)    = VALUE dd07v_tab( ).
*  DATA(lt_domvalue_rres)            = VALUE dd07v_tab( ).
*  DATA(lt_domvalue_nvl_ambiente)    = VALUE dd07v_tab( ).

  DATA(lo_el_context) = wd_context->get_element( ).
  lo_el_context->set_attribute(
    name =  `ENABLED`
    value = abap_false ).

  " Primero, recuperamos todos los dominios
  DATA(lt_domvalue_nivel_riesgo)    = VALUE dd07v_tab( ).
  DATA(lt_domvalue_rres)            = VALUE dd07v_tab( ).
  DATA(lt_dom_status)               = VALUE dd07v_tab( ).
  DATA(lt_clas_indi)                = VALUE dd07v_tab( ).
  DATA(lt_dim_indi)                 = VALUE dd07v_tab( ).
  DATA(lt_tipo_umbral)              = VALUE dd07v_tab( ).
  DATA(lt_tend_indic)               = VALUE dd07v_tab( ).
  DATA(lt_result_eva)               = VALUE dd07v_tab( ).
  DATA(lt_riesgo_inh)               = VALUE dd07v_tab( ).
  DATA(lt_dom_fecuencia)            = VALUE dd07v_tab( ).
  DATA(lt_valor_ambiente)           = VALUE dd07v_tab( ).
* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
  DATA(lt_publicado)                = VALUE dd07v_tab( ).
  DATA(lt_visible_ci)               = VALUE dd07v_tab( ).
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024


  " Recuperamos el dominio del status
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'GRRM_KRI_INST_STATUS'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_dom_status
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio del status
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_PERIODICIDAD'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_dom_fecuencia
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de clase indicador
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_CLASE_INDICADOR'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_clas_indi
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de dimension indicador
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_DIMENSION_INDICADOR'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_dim_indi
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de tipo umbral
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_TIPO_UMBRAL'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_tipo_umbral
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de tendencia indicador
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_TENDENCIA_INDICADOR_N'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_tend_indic
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de resultado evaluación
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_RESUL_EVA_NUM'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_result_eva
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de riesgo inherente
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDE_NIVEL'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_riesgo_inh
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.

  " Recuperamos el dominio de riesgo inherente
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_NIVEL_AMBIENTE_CONTROL'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_valor_ambiente
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.
* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
  " Recuperamos el dominio de publicado
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDM_PUBLICADO'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_publicado
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.


  " Recuperamos el dominio de visible cir
  CALL FUNCTION 'DD_DOMVALUES_GET'
    EXPORTING
      domname        = 'ZDE_VISIBLE_CIR'
      text           = abap_true
    TABLES
      dd07v_tab      = lt_visible_ci
    EXCEPTIONS
      wrong_textflag = 1
      OTHERS         = 2.
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024

* Recuperamos los filtros de la pantalla de selección
  lo_help_general->recuperar_filtros(
    IMPORTING
      et_control             = DATA(lt_control)
      et_process             = DATA(lt_process)
      et_process_lvl_2       = DATA(lt_process_lvl_2)
      et_process_lvl_3       = DATA(lt_process_lvl_3)
      et_process_lvl_4       = DATA(lt_process_lvl_4)
      et_riesgos             = DATA(lt_riesgos)
      et_subprocess          = DATA(lt_subprocess)
      et_subproc_by_lvl_proc = DATA(lt_subproc_by_lvl_proc)
      et_kci                 = DATA(lt_kci)
      ev_control_id          = DATA(lv_control_id)
      ev_proc_id_lvl_1       = DATA(lv_proc_id_lvl_1)
      ev_proc_id_lvl_2       = DATA(lv_proc_id_lvl_2)
      ev_proc_id_lvl_3       = DATA(lv_proc_id_lvl_3)
      ev_proc_id_lvl_4       = DATA(lv_proc_id_lvl_4)
      ev_risk_id             = DATA(lv_risk_id)
      ev_subproc_id          = DATA(lv_subproc_id)
      ev_kci_id              = DATA(lv_kci_id)
      ev_anyo                = DATA(lv_anyo)
      es_periodo             = DATA(ls_periodo)
      ev_anyo_ant            = DATA(lv_anyo_ant)
      es_periodo_ant         = DATA(ls_periodo_ant)
      ) .

  "Eliminamos aquellas líneas que no tengan Subproceso, ya que no tendrán Controles asignados
  DELETE lt_subproc_by_lvl_proc WHERE subprocess_id IS INITIAL.

  IF lv_kci_id IS NOT INITIAL.

    lr_kci   = VALUE #( sign   = 'I'
                       option = 'EQ'
                     (  low    = lv_kci_id ) ) .

  ENDIF.

  IF lv_control_id IS NOT INITIAL.

    lr_control   = VALUE #( sign   = 'I'
                       option = 'EQ'
                     (  low    = lv_control_id ) ) .

  ENDIF.

  IF ls_periodo-id_periodo CS '0SAPM_'.

    lv_month = ls_periodo-id_periodo+6(2).

    lv_date      = lv_anyo && lv_month && '01'.
    lv_first_day = lv_anyo && lv_month && '01'.

  ELSEIF ls_periodo-id_periodo EQ '0SAPY_YEAR'.

    lv_date      = lv_anyo && '1201'.
    lv_first_day = lv_anyo && '0101'.

  ENDIF.

  CALL FUNCTION 'SN_LAST_DAY_OF_MONTH'
    EXPORTING
      day_in       = lv_date
    IMPORTING
      end_of_month = lv_last_day.

  IF ls_periodo_ant-id_periodo CS '0SAPM_'.

    lv_month = ls_periodo_ant-id_periodo+6(2).

    lv_date_ant      = lv_anyo_ant && lv_month && '01'.
    lv_first_day_ant = lv_anyo_ant && lv_month && '01'.

  ELSEIF ls_periodo_ant-id_periodo EQ '0SAPY_YEAR'.

    lv_date_ant      = lv_anyo_ant && '1201'.
    lv_first_day_ant = lv_anyo_ant && '0101'.

  ENDIF.

  CALL FUNCTION 'SN_LAST_DAY_OF_MONTH'
    EXPORTING
      day_in       = lv_date_ant
    IMPORTING
      end_of_month = lv_last_day_ant.

*ZST_CIR_INFORME_KCI_CIR
  DATA lr_kci_id TYPE RANGE OF hrobjid.

  IF lv_proc_id_lvl_4 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING FIELD-SYMBOL(<ls_subproc_by_lvl_proc>)
          WHERE process1_id EQ lv_proc_id_lvl_1
            AND process2_id EQ lv_proc_id_lvl_2
            AND process3_id EQ lv_proc_id_lvl_3
            AND process4_id EQ lv_proc_id_lvl_4.
      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO DATA(ls_aux) WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.

            APPEND INITIAL LINE TO lt_data ASSIGNING FIELD-SYMBOL(<lfs_data>).
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zdesc_indi     = ls_aux-descr.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.


          ENDLOOP.

          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.

          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

    " Se informan 3 niveles de procesos
  ELSEIF lv_proc_id_lvl_3 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
          WHERE process1_id EQ lv_proc_id_lvl_1
            AND process2_id EQ lv_proc_id_lvl_2
            AND process3_id EQ lv_proc_id_lvl_3.
      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


            APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.




          ENDLOOP.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

    " Se informan 2 niveles de procesos
  ELSEIF lv_proc_id_lvl_2 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
          WHERE process1_id EQ lv_proc_id_lvl_1
            AND process2_id EQ lv_proc_id_lvl_2.
      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


            APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.


          ENDLOOP.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

    " Se informa solo el proceso de nivel 1
  ELSEIF lv_proc_id_lvl_1 IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
          WHERE process1_id EQ lv_proc_id_lvl_1.

      " Si tiene subproceso
      IF <ls_subproc_by_lvl_proc>-subprocess_id IS NOT INITIAL.

        " Buscamos si tiene control asociado
        IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

          LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.

            APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
            <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
            <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
            <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
            <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
            <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
            <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
            <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
            <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
            <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
            <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
            <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-control_id.
            <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                    control_id    = ls_aux-control_id ]-descr.



          ENDLOOP.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ELSE.

          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


        ENDIF.

      ENDIF.

    ENDLOOP.

  ELSEIF lv_subproc_id IS NOT INITIAL.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>
        WHERE subprocess_id EQ lv_subproc_id.

      " Buscamos si tiene control asociado
      IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

        LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-control_id.
          <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-descr.



        ENDLOOP.


        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


      ELSE.

        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


      ENDIF.

    ENDLOOP.

  ELSE.

    " Recorremos todos los resultados y vamos rellenando las tablas
    " para filtrar la selección
    LOOP AT lt_subproc_by_lvl_proc ASSIGNING <ls_subproc_by_lvl_proc>.

      " Buscamos si tiene control asociado
      IF line_exists( lt_control[ subprocess_id = <ls_subproc_by_lvl_proc>-subprocess_id ] ).

        LOOP AT lt_control INTO ls_aux WHERE subprocess_id EQ <ls_subproc_by_lvl_proc>-subprocess_id.


          APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
          <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
          <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
          <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
          <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
          <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
          <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
          <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
          <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
          <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
          <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.
          <lfs_data>-zcontrol_rel     = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-control_id.
          <lfs_data>-control_txt    = lt_control[ subprocess_id = ls_aux-subprocess_id
                                                  control_id    = ls_aux-control_id ]-descr.

        ENDLOOP.

        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.


      ELSE.

        APPEND INITIAL LINE TO lt_data ASSIGNING <lfs_data>.
        <lfs_data>-zproc_n1_id    = <ls_subproc_by_lvl_proc>-process1_id.
        <lfs_data>-zproc_n1_txt   = <ls_subproc_by_lvl_proc>-process1_text.
        <lfs_data>-zproc_n2_id    = <ls_subproc_by_lvl_proc>-process2_id.
        <lfs_data>-zproc_n2_txt   = <ls_subproc_by_lvl_proc>-process2_text.
        <lfs_data>-zproc_n3_id    = <ls_subproc_by_lvl_proc>-process3_id.
        <lfs_data>-zproc_n3_txt   = <ls_subproc_by_lvl_proc>-process3_text.
        <lfs_data>-zproc_n4_id    = <ls_subproc_by_lvl_proc>-process4_id.
        <lfs_data>-zproc_n4_txt   = <ls_subproc_by_lvl_proc>-process4_text.
        <lfs_data>-subprocess_id  = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-subprocess_txt = <ls_subproc_by_lvl_proc>-subprocess_title.
        <lfs_data>-zsubproc_id    = <ls_subproc_by_lvl_proc>-subprocess_id.
        <lfs_data>-zsubproc_txt   = <ls_subproc_by_lvl_proc>-subprocess_title.

      ENDIF.

    ENDLOOP.

  ENDIF.


  CALL METHOD lo_amdp->get_kci_cir
    EXPORTING
      im_client     = sy-mandt
      it_kci        = lt_kci
      im_period     = lv_last_day
      im_period_old = lv_last_day_ant
    IMPORTING
      im_kci        = DATA(lt_kci_pro).

  IF lt_kci_pro IS NOT INITIAL.

    SORT lt_kci_pro BY kci_id.

    DATA(lt_kci_pro_eval) = lt_kci_pro[].
    DATA(lt_kci_pro_resp) = lt_kci_pro[].

*        DATA lv_desc TYPE string.
    DATA lv_desc_final TYPE string.
    TYPES: BEGIN OF ltys_desc,
             kci_id TYPE hrp1002-objid,
           END OF ltys_desc.
    DATA lt_kci_aux    TYPE STANDARD TABLE OF ltys_desc.

    lt_kci_aux = CORRESPONDING #( lt_kci ).
*INI DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
*    SELECT  a~objid, b~tabseqnr, b~tline
    SELECT  a~objid, b~tabseqnr, a~begda, a~endda, b~tline, a~tabnr
*FIN DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
     FROM hrp1002 AS a
     INNER JOIN hrt1002 AS b ON a~tabnr EQ b~tabnr
      FOR ALL ENTRIES IN @lt_kci_aux
     WHERE a~objid EQ @lt_kci_aux-kci_id
     AND a~otype EQ 'Z5'
      INTO TABLE @DATA(lt_desc).
*INI DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
*    SORT lt_desc BY objid ASCENDING tabseqnr ASCENDING.
    SORT lt_desc BY objid ASCENDING tabseqnr ASCENDING begda DESCENDING endda DESCENDING.

*    DELETE ADJACENT DUPLICATES FROM lt_kci_pro COMPARING kci_id.
    DELETE ADJACENT DUPLICATES FROM lt_desc COMPARING objid tabseqnr.
*FIN DGL - Incidencia informe KCIs descripciones caducadas 09/07/2024
    " Sacamos los responsables
    SORT lt_kci_pro_resp BY zcontrol_rel zresp_control.
    DELETE ADJACENT DUPLICATES FROM lt_kci_pro_resp COMPARING zcontrol_rel zresp_control.

    LOOP AT lt_kci_pro_resp INTO DATA(ls_kci_pro_resp).

      IF NOT line_exists( lt_resp[ id_control = ls_kci_pro_resp-zcontrol_rel ] ).

        APPEND INITIAL LINE TO lt_resp ASSIGNING FIELD-SYMBOL(<lfs_resp>).
        <lfs_resp>-id_control = ls_kci_pro_resp-zcontrol_rel.
        <lfs_resp>-resp = REDUCE #( INIT lv_resp TYPE grfn_text
                          FOR  ls_control_aux IN lt_kci_pro_resp
                          WHERE ( zcontrol_rel = ls_kci_pro_resp-zcontrol_rel )
                          NEXT lv_resp = COND #( WHEN lv_resp IS INITIAL
                                                 THEN ls_control_aux-zresp_control
                                                 ELSE lv_resp && ',' && ls_control_aux-zresp_control ) ).

      ENDIF.

    ENDLOOP.

    LOOP AT lt_kci INTO DATA(ls_kci).

      ls_alv_kci-zid_kci = ls_kci-kci_id.
      ls_alv_kci-zid_risk = ls_kci-control_id.

      DATA lv_numero TYPE p LENGTH 16 DECIMALS 2.

      READ TABLE lt_kci_pro ASSIGNING FIELD-SYMBOL(<fs_kci_pro>) WITH KEY kci_id = ls_kci-kci_id.
      IF sy-subrc EQ 0.
        MOVE-CORRESPONDING <fs_kci_pro> TO ls_alv_kci.

        lv_numero = <fs_kci_pro>-zvalor_num_eur.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_num_n.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_n CURRENCY 'EUR'.

        MOVE <fs_kci_pro>-zumb_min_n TO lv_numero.
        WRITE lv_numero TO ls_alv_kci-zumb_min_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zumb_max_n.
        WRITE lv_numero TO ls_alv_kci-zumb_max_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zumb_min_eur.
        WRITE lv_numero TO ls_alv_kci-zumb_min_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zumb_max_eur.
        WRITE lv_numero TO ls_alv_kci-zumb_max_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_n.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_eur.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_n.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_n CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_eur.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_eur CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_num_eur_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_eur_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_eur_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_eur_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_eur_ant.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_eur_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_den_n_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_den_n_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zvalor_num_n_ant.
        WRITE lv_numero TO ls_alv_kci-zvalor_num_n_ant CURRENCY 'EUR'.

        lv_numero = <fs_kci_pro>-zresul_indi_n_ant.
        WRITE lv_numero TO ls_alv_kci-zresul_indi_n_ant CURRENCY 'EUR'.

      ENDIF.

      READ TABLE lt_data INTO DATA(ls_data) WITH KEY zcontrol_rel = <fs_kci_pro>-zcontrol_rel.
      IF sy-subrc EQ 0.

        ls_alv_kci-zproc_n1_id      = ls_data-zproc_n1_id.
        ls_alv_kci-zproc_n1_txt     = ls_data-zproc_n1_txt.
        ls_alv_kci-zproc_n2_id      = ls_data-zproc_n2_id.
        ls_alv_kci-zproc_n2_txt     = ls_data-zproc_n2_txt.
        ls_alv_kci-zproc_n3_id      = ls_data-zproc_n3_id.
        ls_alv_kci-zproc_n3_txt     = ls_data-zproc_n3_txt.
        ls_alv_kci-zproc_n4_id      = ls_data-zproc_n4_id.
        ls_alv_kci-zproc_n4_txt     = ls_data-zproc_n4_txt.
        ls_alv_kci-zsubproc_id      = ls_data-zsubproc_id.
        ls_alv_kci-zsubproc_txt     = ls_data-zsubproc_txt.
        ls_alv_kci-zyear_act        = lv_anyo.
        ls_alv_kci-zperiod_act      = ls_periodo-periodo.
        ls_alv_kci-zyear_ant        = lv_anyo_ant.
        ls_alv_kci-zperiod_ant      = ls_periodo_ant-periodo.
*        ls_alv_kci-zamb_control     = <fs_kci_pro>-zamb_control.
*        ls_alv_kci-zamb_control_ant = <fs_kci_pro>-zamb_control_ant.

        ls_alv_kci-zdesc_indi   = REDUCE #( INIT lv_desc TYPE string
                          FOR  ls_desc IN lt_desc
                          WHERE ( objid = ls_kci-kci_id )
                          NEXT lv_desc = COND #( WHEN lv_desc IS INITIAL
                                                 THEN ls_desc-tline
                                                 ELSE lv_desc && ' ' && ls_desc-tline ) ).

        ls_alv_kci-zdesc_indi = replace( val   = ls_alv_kci-zdesc_indi
                                         regex = cl_abap_char_utilities=>horizontal_tab
                                         with  = ''
                                         occ   = 0 ).

        ls_alv_kci-znom_indi    = <fs_kci_pro>-znom_indi.
*        ls_alv_kci-zid_kci      = <fs_kci_pro>-kci_id.

        ls_alv_kci-zestado            = VALUE #( lt_dom_status[ domvalue_l = <fs_kci_pro>-zestado            " Estado
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
        ls_alv_kci-zpublicado           = VALUE #( lt_publicado[ domvalue_l = <fs_kci_pro>-zpublicado         " Publicado
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).
        IF  <fs_kci_pro>-zvisible_ci IS NOT INITIAL.
          ls_alv_kci-zvisible_ci         = 'Si'.        " Visible CI
        ELSE.
          ls_alv_kci-zvisible_ci         = 'No' .        " Visible CI
        ENDIF.


* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024

        ls_alv_kci-zclase_indi        = VALUE #( lt_clas_indi[ domvalue_l = <fs_kci_pro>-zclase_indi         " Clase Indicador
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zdimen_indi        = VALUE #( lt_dim_indi[ domvalue_l = <fs_kci_pro>-zdimen_indi          " Dimension Indicador
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).
        IF <fs_kci_pro>-zdimen_indi EQ 01.
          " EUROS
          CLEAR:
          <fs_kci_pro>-zvalor_num_eur,
          <fs_kci_pro>-zvalor_den_eur,
          <fs_kci_pro>-zresul_indi_eur,
          <fs_kci_pro>-ztend_ind_eur,
          <fs_kci_pro>-zresul_eva_eur,
          <fs_kci_pro>-zumb_min_eur,
          <fs_kci_pro>-zumb_max_eur,
          <fs_kci_pro>-zvalor_num_eur_ant,
          <fs_kci_pro>-zvalor_den_eur_ant,
          <fs_kci_pro>-zresul_indi_eur_ant,

          ls_alv_kci-zvalor_num_eur,
          ls_alv_kci-zvalor_den_eur,
          ls_alv_kci-zresul_indi_eur,
          ls_alv_kci-ztend_ind_eur,
          ls_alv_kci-zumb_min_eur,
          ls_alv_kci-zumb_max_eur,
          ls_alv_kci-zresul_eva_eur,
          ls_alv_kci-zvalor_num_eur_ant,
          ls_alv_kci-zresul_indi_eur_ant,
          ls_alv_kci-zvalor_den_eur_ant.

        ELSEIF <fs_kci_pro>-zdimen_indi EQ 02.
          " NUMEROS
          CLEAR:
          <fs_kci_pro>-zresul_eva_n,
          <fs_kci_pro>-zvalor_num_n,
          <fs_kci_pro>-zvalor_den_n,
          <fs_kci_pro>-zresul_indi_n,
          <fs_kci_pro>-ztend_ind_n,
          <fs_kci_pro>-zumb_min_n,
          <fs_kci_pro>-zumb_max_n,
          <fs_kci_pro>-zvalor_den_n_ant,
          <fs_kci_pro>-zvalor_num_n_ant,
          <fs_kci_pro>-zresul_indi_n_ant,

          ls_alv_kci-zvalor_num_n,
          ls_alv_kci-zvalor_den_n,
          ls_alv_kci-zresul_indi_n,
          ls_alv_kci-ztend_ind_n,
          ls_alv_kci-zumb_min_n,
          ls_alv_kci-ztend_ind_n,
          ls_alv_kci-zumb_max_n,
          ls_alv_kci-zvalor_den_n_ant,
          ls_alv_kci-zvalor_num_n_ant,
          ls_alv_kci-zresul_indi_n_ant.

        ENDIF.

        ls_alv_kci-ztipo_umbral       = VALUE #( lt_tipo_umbral[ domvalue_l = <fs_kci_pro>-ztipo_umbral      " Tipo Umbral
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_n        = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_n        " Tendencia indicador n
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_eur      = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_eur      " Tendencia indicador eur
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_n_ant    = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_n_ant    " Tendencia indicador n anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-ztend_ind_eur_ant  = VALUE #( lt_tend_indic[ domvalue_l = <fs_kci_pro>-ztend_ind_eur_ant  " Tendencia indicador eur anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_n       = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_n       " Resultado evaluación N
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_eur     = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_eur     " Resultado evaluación EUR
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_n_ant   = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_n_ant   " Resultado evaluación N anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zresul_eva_eur_ant = VALUE #( lt_result_eva[ domvalue_l = <fs_kci_pro>-zresul_eva_eur_ant " Resultado evaluación EUR anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

        ls_alv_kci-zamb_control       = VALUE #( lt_valor_ambiente[ domvalue_l = <fs_kci_pro>-zamb_control     " Ambiente de control
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
        ls_alv_kci-zres_amb_control     = <fs_kci_pro>-zres_amb_control.   " Resultado Ambiente de control
        ls_alv_kci-zval_amb_control     = <fs_kci_pro>-zval_amb_control.   " Valor Ambiente de control
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024

        ls_alv_kci-zamb_control_ant   = VALUE #( lt_valor_ambiente[ domvalue_l = <fs_kci_pro>-zamb_control_ant " Ambiente de control anterior
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024
        ls_alv_kci-zres_amb_control_ant     = <fs_kci_pro>-zres_amb_control_ant.   " Resultado Ambiente de control anterior
        ls_alv_kci-zval_amb_control_ant     = <fs_kci_pro>-zval_amb_control_ant.   " Valor Ambiente de control anterior
* FIN MCR - PPM100531913 - Nuevos campos informes CIR 06/09/2024


        ls_alv_kci-zfrec_medida       = VALUE #( lt_dom_fecuencia[ domvalue_l = <fs_kci_pro>-zfrec_medida    " Frecuencia medida
                                                       ddlanguage = sy-langu ]-ddtext OPTIONAL ).

* INI JAGM 25.04.2023 - Incidencia Visibilidad TODOS los KCIs/KRIs(solo debe ver los suyos)
      ELSE.
        CONTINUE.
* FIN JAGM 25.04.2023 - Incidencia Visibilidad TODOS los KCIs/KRIs(solo debe ver los suyos)

      ENDIF.

      READ TABLE lt_resp INTO DATA(ls_resp) WITH KEY id_control = <fs_kci_pro>-zcontrol_rel.
      IF sy-subrc EQ 0.
        DATA lv_control_rel TYPE string.

        ls_alv_kci-zresp_control = ls_resp-resp.

        SELECT SINGLE stext
          FROM hrp1000
          INTO lv_control_rel
          WHERE objid = <fs_kci_pro>-zcontrol_rel
          AND otype = 'P2'.

        ls_alv_kci-zcontrol_rel = lv_control_rel.

        CLEAR lv_control_rel.


      ENDIF.
      APPEND ls_alv_kci TO lt_alv_kci.
      CLEAR ls_alv_kci.
    ENDLOOP.

    IF lr_kci IS NOT INITIAL.

      DELETE lt_alv_kci WHERE zid_kci NOT IN lr_kci.

    ENDIF.

    IF lr_control IS NOT INITIAL.

      DELETE lt_alv_kci WHERE zid_risk NOT IN lr_control.

    ENDIF.



    SORT lt_alv_kci BY     zproc_n1_id    ASCENDING
                           zproc_n2_id    ASCENDING
                           zproc_n3_id    ASCENDING
                           zproc_n4_id    ASCENDING.

    DATA(lt_data_informe) = VALUE wd_comp_controller->elements_data( ).
    DATA(lo_data_informe) = wd_context->get_child_node( wd_this->wdctx_data ).

    lt_data_informe = CORRESPONDING #( lt_alv_kci ).

    lo_data_informe->invalidate( ).

    IF lt_data_informe IS NOT INITIAL.

      lo_data_informe->bind_table( EXPORTING new_items = lt_data_informe ).

    ENDIF.

  ENDIF.

ENDMETHOD.

method ONACTIONTOGGLE_SELECTION .

    wd_comp_controller->show_selection( CONV #( wdevent->get_char( 'CHECKED' ) ) ).

endmethod.

endclass.

