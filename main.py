import json
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

auto_increment_product_key = 0
auto_increment_order_id = 0

class ProductRequest(BaseModel):
    value: str


class ProductNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class Product:
    def __init__(self):
        self.root = None

    def insert(self, key, value):

        """
        Inserta un nodo en el árbol con la clave y valor especificados.
        
        :param key: Clave del nodo a insertar.
        :type key: int
        :param value: Valor del nodo a insertar.
        :type value: str
        :raises ValueError: Si la clave ya existe en el árbol.
        """
        if not self.root:
            self.root = ProductNode(key, value)
        else:
            self._insert(self.root, key, value)

    def _insert(self, current, key, value):
        """
        Inserta un nodo en el árbol con la clave especificada.

        :param current: Nodo actual en el que se encuentra el árbol.
        :type current: ProductNode
        :param key: Clave del nodo a insertar.
        :type key: int
        :param value: Valor del nodo a insertar.
        :type value: str
        :raises ValueError: Si la clave ya existe en el árbol.
        """
        if key < current.key:
            if not current.left:
                current.left = ProductNode(key, value)
            else:
                self._insert(current.left, key, value)
        elif key > current.key:
            if not current.right:
                current.right = ProductNode(key, value)
            else:
                self._insert(current.right, key, value)
        else:
            # Si la clave existe, lanzamos una excepción
            raise ValueError("Clave duplicada.")

    def search(self, key):
        """
        Busca el valor de la clave especificada en el árbol BST.

        :param key: Clave del nodo a buscar.
        :type key: int
        :return: Valor del nodo con la clave especificada, o None si no existe.
        """
        return self._search(self.root, key)

    def _search(self, current, key):
        """
        Busca el valor de la clave especificada en el árbol BST.

        :param current: Nodo actual en el recorrido.
        :type current: ProductNode
        :param key: Clave del nodo a buscar.
        :type key: int
        :return: Valor del nodo con la clave especificada, o None si no existe.
        :rtype: str or None
        """
        if not current:
            return None
        elif key == current.key:
            return current.value
        elif key < current.key:
            return self._search(current.left, key)
        else:
            return self._search(current.right, key)

    def update(self, key, new_value):
        """
        Actualiza el valor del nodo con la clave especificada.

        :param key: Clave del nodo a actualizar.
        :type key: int
        :param new_value: Nuevo valor del nodo.
        :type new_value: str
        :return: True si se actualizó el nodo, False si no existe el nodo con la clave especificada.
        :rtype: bool
        """
        node = self._search_node(self.root, key)
        if node:
            node.value = new_value
            return True
        return False

    def _search_node(self, current, key):
        """
        Busca el nodo con la clave especificada en la BST y devuelve
        el nodo encontrado o None si no existe.

        :param current: Nodo actual en el recorrido.
        :type current: ProductNode
        :param key: Clave del nodo a buscar.
        :type key: int
        :return: El nodo con la clave especificada o None si no existe.
        :rtype: ProductNode
        """
        if not current:
            return None
        if key == current.key:
            return current
        elif key < current.key:
            return self._search_node(current.left, key)
        else:
            return self._search_node(current.right, key)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, current, key):
        """
        Elimina el nodo de la BST que contiene la clave especificada y devuelve el nuevo nodo raíz.

        Si el nodo a eliminar tiene dos hijos, se reemplaza por el nodo que se encuentra en el camino
        más a la izquierda del nodo derecho (sucesor inorden).

        :param current: Nodo actual en el recorrido.
        :type current: ProductNode
        :param key: Clave del nodo a eliminar.
        :type key: int
        :return: El nuevo nodo raíz de la BST.
        :rtype: ProductNode
        """
        if not current:
            return None

        if key < current.key:
            current.left = self._delete(current.left, key)
        elif key > current.key:
            current.right = self._delete(current.right, key)
        else:
            if not current.left:
                return current.right
            elif not current.right:
                return current.left

            successor = current.right
            while successor.left:
                successor = successor.left

            current.key = successor.key
            current.value = successor.value
            current.right = self._delete(current.right, successor.key)

        return current

    def list(self):
        """
        Devuelve una lista con los pares clave-valor de los nodos de la BST,
        ordenados en orden inorden (izquierda-raíz-derecha).

        :return: Lista con los pares clave-valor.
        """
        result = []

        def _inorder(node):
            if node:
                _inorder(node.left)
                result.append({"key": node.key, "value": node.value})
                _inorder(node.right)

        _inorder(self.root)
        return result


product_bst = Product()


@app.post("/products")
def create_product(product_request: ProductRequest):
    """
    Crea un nuevo producto en la base de datos.

    Args:
        product_request (ProductRequest): Información del producto a crear.

    Returns:
        dict: Un diccionario con un mensaje de confirmación y el producto creado.

    Raises:
        HTTPException: Si el producto ya existe en la base de datos.
    """

    global auto_increment_product_key

    new_key = auto_increment_product_key +  1
    auto_increment_product_key = new_key

    try:
        product_bst.insert(new_key, product_request.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "message": "Producto creado correctamente",
        "product": get_product(new_key),
    }


@app.get("/products/{key}")
def get_product(key: int):
    """
    Obtiene el producto con la clave especificada.

    Args:
        key (int): Clave del producto a obtener.

    Returns:
        dict: Un diccionario con la clave y el valor del producto.

    Raises:
        HTTPException: Si el producto no existe.
    """

    value = product_bst.search(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"key": key, "value": value}


@app.put("/products/{key}")
def update_product(key: int, product_request: ProductRequest):
    """
    Actualiza el producto con la key especificada.

    Args:
        key (int): Key del producto a actualizar.
        product_request (ProductRequest): Información del producto a actualizar.

    Returns:
        Un mensaje de confirmación de actualización y el producto actualizado.

    Raises:
        HTTPException: Si el producto no existe.
    """
    updated = product_bst.update(key, product_request.value)
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "message": "Producto actualizado correctamente",
        "product": get_product(key),
    }


@app.delete("/products/{key}")
def delete_product(key: int):
    """
    Elimina el producto con la key especificada.

    Args:
        key (int): Key del producto a eliminar.

    Returns:
        Un mensaje de confirmación de eliminación.

    Raises:
        HTTPException: Si el producto no existe.
    """
    existing = product_bst.search(key)
    if existing is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product_bst.delete(key)
    return {"message": "Producto eliminado correctamente"}


@app.get("/products")
def list_products():
    """
    Devuelve una lista de todos los productos en el sistema.

    Returns:
        list: Una lista de diccionarios, cada uno conteniendo la 'key' y 'value'
        de un producto almacenado.
    """

    return product_bst.list()


class OrderRequest(BaseModel):
    products: List[int] = []


class OrderNode:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self.next = None


class Order:
    def __init__(self):
        self.head = None
        self.length = 0

    def add(self, id, data):
        """
        Agrega un nuevo nodo de orden al final de la lista.

        Args:
            id (int): Identificador único de la orden.
            data (str): Datos asociados a la orden.

        """
        new_node = OrderNode(id, data)
        if not self.head:
            self.head = new_node
            self.length += 1
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
            self.length += 1

    def find(self, id):
        """
        Busca y devuelve los datos de la orden con el id especificado en la lista enlazada.

        Args:
            id (int): Identificador único de la orden a buscar.

        Returns:
            str: Datos asociados a la orden si se encuentra, de lo contrario None.
        """
        current = self.head
        while current:
            if current.id == id:
                return current.data
            current = current.next
        return None

    def delete(self, id):
        """
        Elimina la orden con el id especificado de la lista enlazada.

        Args:
            id (int): Identificador único de la orden a eliminar.

        Returns:
            None
        """
        if not self.head:
            return
        if self.head.id == id:
            self.head = self.head.next
            self.length -= 1
            return
        current = self.head
        while current.next:
            if current.next.id == id:
                current.next = current.next.next
                self.length -= 1
                return
            current = current.next
        return None

    def update(self, id, data):
        """
        Actualiza la orden con el id especificado con los nuevos datos.

        Args:
            id (int): Identificador único de la orden a actualizar.
            data (str): Nuevos datos asociados a la orden.

        Returns:
            bool: True si se actualizó la orden, False si no se encontró.
        """
        current = self.head
        while current:
            if current.id == id:
                current.data = data
                return True
            current = current.next
        return False

    def list(self):
        """
        Obtiene una lista con los datos de todas las órdenes en la lista enlazada.

        Returns:
            list: Una lista que contiene los datos de todas las órdenes.
        """

        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result


order_list = Order()


@app.post("/orders")
def create_order(order_request: OrderRequest):

    """
    Crea una nueva orden con los productos especificados.

    Args:
        order_request (OrderRequest): Información de la orden a crear.

    Returns:
        Un mensaje de confirmación de creación y la orden creada.

    Raises:
        HTTPException: Si la orden ya existe o si alguno de los productos no existen.
    """
    global auto_increment_order_id

    new_id = auto_increment_order_id + 1
    auto_increment_order_id = new_id

    existing = order_list.find(new_id)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Ya existe una orden con ese ID.")

    products_data = []
    for key in order_request.products:
        product_value = product_bst.search(key)
        if product_value is None:
            raise HTTPException(
                status_code=404,
                detail=f"El producto con key={key} no existe en el BST.",
            )

        products_data.append({"key": key, "value": product_value})

    order_data = {"id": new_id, "products": products_data}
    order_list.add(new_id, order_data)

    return {"message": "Orden creada correctamente", "order": order_data}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    """
    Obtiene la orden con el id especificado.

    Args:
        order_id (int): Identificador de la orden a buscar.

    Returns:
        dict: La información (id, products, etc.) de la orden.

    Raises:
        HTTPException: Si la orden no existe.
    """
    order_data = order_list.find(order_id)
    if not order_data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order_data


@app.put("/orders/{order_id}")
def update_order(order_id: int, order_request: OrderRequest):
    """
    Actualiza una orden existente con los productos especificados.

    Args:
        order_id (int): ID de la orden a actualizar.
        order_request (OrderRequest): Información de la orden a actualizar.

    Returns:
        Un mensaje de confirmación de actualización y la orden actualizada.

    Raises:
        HTTPException: Si la orden no existe o si alguno de los productos no existen.
    """
    existing_order = order_list.find(order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    new_products_data = []
    for key in order_request.products:
        product_value = product_bst.search(key)
        if product_value is None:
            raise HTTPException(
                status_code=404,
                detail=f"El producto con key={key} no existe en el BST.",
            )
        new_products_data.append({"key": key, "value": product_value})

    order_data = {"id": order_id, "products": new_products_data}

    updated = order_list.update(order_id, order_data)
    if not updated:
        raise HTTPException(status_code=404, detail="No se pudo actualizar la orden")

    return {"message": "Orden actualizada correctamente", "order": order_data}


@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    """
    Elimina la orden con el id especificado.

    Args:
        order_id (int): ID de la orden a eliminar.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException: Si la orden no existe.
    """
    order_data = order_list.find(order_id)
    if not order_data:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    order_list.delete(order_id)
    return {"message": "Orden eliminada correctamente"}


@app.get("/orders")
def list_orders():
    """
    Lista todas las órdenes almacenadas en la lista enlazada.

    Returns:
        list: Lista de órdenes (cada orden es un dict con id y products).
    """
    return order_list.list()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)

