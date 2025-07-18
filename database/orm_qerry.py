import math
from sqlalchemy import select, update, delete
from database.models import Product, Banner, Cart, Category, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


# Простой пагинатор
class Paginator:
    def __init__(self, array: list | tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        # math.ceil - округление в большую сторону до целого числа
        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_items = self.__get_slice()
        return page_items

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError(f"Next page does not exist. Use has_next() to check before.")

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError(
            f"Previous page does not exist. Use has_previous() to check before."
        )


############### Работа с баннерами (информационными страницами) ###############


async def orm_add_banner_description(session: AsyncSession, data: dict):
    # добавление нового или изменение существующего банера
    # из пунктов : main,  about,  cart, shipping, payment, catalog
    querry = select(Banner)
    result = await session.execute(querry)
    if result.first():
        return
    session.add_all(
        [
            Banner(name=name, description=description)
            for name, description in data.items()
        ]
    )
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    result = await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


############### КАТЕГОРИИ ###############


# получить все категории
async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


# создать категории
async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


# Добавление новой категории
async def orm_add_new_category(session:AsyncSession, name:str):
    query = select(Category).where(Category.name == name)
    result = await session.execute(query)
    if result.first():
        return
    session.add(Category(name=name))
    await session.commit()

# Удаление категорий всех
# удаление тех категорий которе нужны были для запуска бота 
# добавление новых категорий до того как загружать товары 
async def orm_delete_all_old_categories(session:AsyncSession):
    query = delete(Category)
    await session.execute(query)
    await session.commit()

# Удаление категории по имени 

async def orm_delete_categpry_on_name(session:AsyncSession, name:str):
    query = delete(Category).where(Category.name == name)
    await session.execute(query)
    await session.commit()
    

##########################Админка добавить/изменить/удалить товары ######################################


# добавление нового товара
async def orm_add_product(data: dict, session: AsyncSession):
    obj = Product(
        name=data["name"],
        description=data["description"],
        category_id=int(data["category"]),
        price=float(data["price"]),
        image=data["image"],
    )

    session.add(obj)
    await session.commit()


async def orm_get_category_products(session: AsyncSession, category_id):
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image=data["image"],
            category_id=int(data["category"]),
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


#################################### ДОБАВЛЕНИЕ USER В БАЗУ ДАННЫЙХ ####################################


async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(
                user_id=user_id, first_name=first_name, last_name=last_name, phone=phone
            )
        )
    await session.commit()


#################################### Работа с Корзинами ####################################
# Добавление товара в корзину
async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    query = (
        select(Cart)
        .where(Cart.user_id == user_id, Cart.product_id == product_id)
        .options(joinedload(Cart.product))
    )
    result = await session.execute(query)
    cart = result.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:  # попробовать удалить else
        cart = Cart(user_id=user_id, product_id=product_id, quantity=1)
        session.add(cart)
        await session.commit()


async def orm_get_user_carts(session: AsyncSession, user_id: int):
    query = (
        select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(
    session: AsyncSession, user_id: int, product_id: int
):
    query = (
        select(Cart)
        .where(Cart.user_id == user_id, Cart.product_id == product_id)
        .options(joinedload(Cart.product))
    )
    cart = await session.execute(query)
    cart: Cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(
            session=session, user_id=user_id, product_id=product_id
        )
        await session.commit()
        return False


async def orm_delete_all_carts_user(session: AsyncSession, user_id: int):
    query = delete(Cart).where(Cart.user_id == user_id)
    await session.execute(query)
    await session.commit()
