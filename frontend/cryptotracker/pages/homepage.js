import Card from "../comps/Card";
const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {

    const [data, setData] = useState([])
    const [isLoading, setLoading] = useState(false)
    useEffect(() => {
        fetch('http://localhost:5000/coinpairs')
            .then((res) => res.json())
            .then((data) => {
                let coinpairs = data.coinpairs
                setData(coinpairs)
                setLoading(false)
            })
    }, [])

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    return (
        <div>
            Cards
            {data.map((coin) =>{return <Card coinpair_sym={coin.coinpair_sym}
                      price_update={coin.coinpair_price.insert_time}
                      price_value={coin.coinpair_price.price}/>})}
        </div>
    )
}
export default Homepage