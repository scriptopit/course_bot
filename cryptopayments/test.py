import asyncio

from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.models.invoice import PaidButtons


crypto = AioCryptoPay(token="7284:AAPk3szHxhvWU7Oo6pCJbBh6bTZycQwicff", network=Networks.TEST_NET)


async def main():
    invoice = await crypto.create_invoice(
        asset="USDT",
        amount=1,
        description="Оплата курсов Pythonic Bytes",
        paid_btn_name="openChannel",
        paid_btn_url="https://t.me/pybytes",
        expires_in=18000,
        hidden_message="Поздравляем с приобретением курса, "
                       "надеемся что твой путь будет легкий и полный удач."
                       "\nТвоим куратором будет @python_devss"
    )
    print(invoice.pay_url)
    print(invoice.status)


if __name__ == '__main__':
    asyncio.run(main())

