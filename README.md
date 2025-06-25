# Universalis API wrapper
- A simple and light weight wrapper for [Universalis](https://universalis.app) marketboard information.


See https://docs.universalis.app/ for more information.



### Example

```py
import aiohttp
from universalis import UniversalisAPI, CurrentData, HistoryData

async def sample() -> None:
    item_id = 14 # Fire Cluster
    # You only need to pass in a aiohttp.ClientSession if 
    # you already have one you are using elsewhere in your code base.
    session = aiohttp.ClientSession()
    universalis = UniversalisAPI(session=session)
    cur_data: CurrentData = await universalis.get_current_data(item=item_id)
```
