import asyncio
import random


async def main():
    # 协程池
    coro_pool = set()
    task_id = 0

    while True:
        while len(coro_pool) < 5:
            # 创建协程
            task_id = task_id + 1
            coro = create_end_coro(task_id)
            coro_pool.add(asyncio.create_task(coro))

            print('当前协程池中的协程数量:', len(coro_pool))

        done, pending = await asyncio.wait(coro_pool, return_when=asyncio.FIRST_COMPLETED)
        coro_pool = pending


async def create_end_coro(task_id):
    print(f'协程{task_id}开始')
    time = random.randint(1, 3)
    await asyncio.sleep(time)
    print(f'协程{task_id}结束,耗时{time}秒')


if __name__ == '__main__':
    asyncio.run(main())
