import Card from "../comps/coinpairCard/Card.js";
const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {

    const [data, setData] = useState()
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
            <div id="Cards">
                {data.map((coin) =>{return <Card coinpair_id={coin.coinpair_id}
                    coinpair_sym={coin.coinpair_sym}
                    price_update={coin.coinpair_price.insert_time}
                    price_value={coin.coinpair_price.price}/>})}
            </div>
            <div id="modal-root"></div>

        </div>
    )
};
export default Homepage