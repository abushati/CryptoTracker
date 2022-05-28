import { Router, useRouter } from "next/router";
const {useEffect} = require("react");
const {useState} = require("react");
import { API } from "../../config";
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import RemoveIcon from '@mui/icons-material/Remove';
import { Line } from "react-chartjs-2";
import Chart from 'chart.js/auto';

function CoinPair () {
    const router = useRouter();  
    const [data, setData] = useState([])
    const [graphData,setGraphData] = useState({})
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

    const createGraph = (data) => {

        let hourValues = data.coinpair_history.hour_values

        let fillColor = ''
        if (hourValues[0].price > hourValues[hourValues.length-1].price) {
            fillColor = '#ff000057'
        } else {
            fillColor = '#00ff237a'
        }
        setGraphData({
            labels: data.coinpair_history.hour_values.map((data) => data.insert_time),
            datasets: [
              {
                label: "Price in USD",
                data: data.coinpair_history.hour_values.map((data) => data.price),
                backgroundColor: [
                  "#ffbb11",
                  "#ecf0f1",
                  "#50AF95",
                  "#f3ba2f",
                  "#2a71d0"
                ],
                fill:{
                    target: 'origin',
                    above: fillColor,   // Area will be red above the origin
                }
              }
            ]
            
          });
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
                createGraph(data)
                setIsLoaded(true)
            })

    }, [router.isReady]);
 
    if (!isLoaded) return <p>Loading...</p>
    return (
        <div>
            <div>{data.coinpair_sym}</div>
            <div>Current Price: ${data.coinpair_price.price}</div>
            <div>Last Update {data.coinpair_price.insert_time}</div>
            <div style={{display:'flex'}}>
                <div style={{whiteSpace:'nowrap'}}>
                    <table>
                        <tr>
                            <th>Time</th>
                            <th>Price</th>
                            <th>Direction</th>
                        </tr>
                        {hourRows.map(row => row)}
                    </table>
                </div>
                <div style={{width: '80vw'}}>

                    <Line
                        data={graphData}
                        options={{
                            plugins: {
                                title: {
                                display: true,
                                text: "Cryptocurrency prices"
                                },
                                legend: {
                                display: true,
                                position: "bottom"
                            }
                            }
                        }}
                    />
                </div>
            </div>
        </div>
    )
};
export default CoinPair