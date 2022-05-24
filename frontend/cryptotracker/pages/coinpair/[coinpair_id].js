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
    const [hourRow, setHourRows] = useState([])
    const [isLoaded, setIsLoaded] = useState(false)

    function hourRows(hourData){
        return hourData.map(row => { 
            return `<tr>
                <td>
                    ${row.insert_time}
                </td>
                <td>
                    ${row.price}
                </td>
                <td>
                    <i className="fa fa-arrow-up" />
                </td>
            </tr>`
        })
    }
    //Todo: To create the table here and not inline in the return state NOTE: the most recent price insert is currently at the bottom
    let setUpTable = () => {
        
    }

    useEffect(() => {
        console.log(router.isReady)
        if (!router.isReady) return;
        let coinpairId = router.query.coinpair_id
        console.log(coinpairId)
        fetch(`http://${API}/coinpair/${coinpairId}`)
            .then((res) => res.json())
            .then((data) => {
                setData(data)
                console.log(data)
                // let lastHourPriceHistory = lastHourPriceRows(data.coinpair_history[0].hour_values)
                setHourRows(data.coinpair_history.hour_values)
                setUpTable()
                setIsLoaded(true)
                // console.log(lastHourPriceHistory)
            })

    }, [router.isReady]);
 
    if (!isLoaded) return <p>Loading...</p>
    return (
        <div>
            'Hi from coin pair page'
            <div>{data.coinpair_sym}</div>
            <div>Current Price: ${data.coinpair_price.price}</div>
            <div>Last Update {data.coinpair_price.insert_time}</div>

            <table>
                <tr>
                    <th>Time</th>
                    <th>Price</th>
                    <th>Direction</th>
                </tr>
                {hourRow.map((row,index,rows) => {
                    return (
                        <tr>
                            <td>
                                {row.insert_time}
                            </td>
                            <td>
                                {row.price}
                            </td>
                            <td> 
                                {index == 0 ||  rows[index-1].price == row.price?
                                    <RemoveIcon style={{color:"grey"}}/> :
                                index > 1 && rows[index-1].price > row.price ?
                                    <ArrowUpwardIcon style={{color:"green"}}/> :
                                    <ArrowDownwardIcon style={{color:"red"}}/> } 
                            </td>
                        </tr>
                )})}
            </table>
        </div>
    )
};
export default CoinPair