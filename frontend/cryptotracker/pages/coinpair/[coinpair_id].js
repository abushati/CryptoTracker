import { Router, useRouter } from "next/router";
const {useEffect} = require("react");
const {useState} = require("react");
import { API } from "../../config";
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import RemoveIcon from '@mui/icons-material/Remove';

function CoinPair () {
    const router = useRouter();  
    const [data, setData] = useState([])
    const [hourRows, setHourRows] = useState([])
    const [isLoaded, setIsLoaded] = useState(false)

    //Todo: To create the table here and not inline in the return state NOTE: the most recent price insert is currently at the bottom
    let setUpTable = (hourData) => {
        let lastDataIndex = hourData.length - 1
        let rows = hourData.map((row,index,rows) => {
            return (
                <tr>
                    <td>
                        {row.insert_time}
                    </td>
                    <td>
                        {row.price}
                    </td>
                    <td> 
                        {index == lastDataIndex ||  rows[index+1].price == row.price?
                            <RemoveIcon style={{color:"grey"}}/> :
                        index > 1 && rows[index+1].price > row.price ?
                            <ArrowDownwardIcon style={{color:"red"}}/>:                             
                            <ArrowUpwardIcon style={{color:"green"}}/>} 
                    </td>
                </tr>
                )
            }
        )
        return rows
    }

    useEffect(() => {
        if (!router.isReady) return;
        let coinpairId = router.query.coinpair_id
        console.log(coinpairId)
        fetch(`http://${API}/coinpair/${coinpairId}`)
            .then((res) => res.json())
            .then((data) => {
                setData(data)                
                let hourRows = setUpTable(data.coinpair_history.hour_values)
                setHourRows(hourRows)
                setIsLoaded(true)
            })

    }, [router.isReady]);
 
    if (!isLoaded) return <p>Loading...</p>
    return (
        <div>
            <div>{data.coinpair_sym}</div>
            <div>Current Price: ${data.coinpair_price.price}</div>
            <div>Last Update {data.coinpair_price.insert_time}</div>

            <table>
                <tr>
                    <th>Time</th>
                    <th>Price</th>
                    <th>Direction</th>
                </tr>
                {hourRows.map(row => row)}
            </table>
        </div>
    )
};
export default CoinPair