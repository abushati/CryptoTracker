import Card from "../comps/coinpairCard/Card.js";
const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {

    const [data, setData] = useState()
    const [userWatchlist, setUserWatchlist] = useState()
    // const [setWatchlistIds, setWatchlistIds] = useState()
    const [user, setuser] = useState()
    const [alerts, setAlerts] = useState()
    const [isLoading, setLoading] = useState(false)
    
    const updateWatchlist = (action,coinpairId) => {
        console.log(coinpairId)
        if (action=='remove') {
            let updated = userWatchlist.coinpairs.filter((e) => e.coinpair_id != coinpairId)        
            console.log(updated)
            setUserWatchlist({'coinpairs':updated})
          }
    }


    useEffect(() => {
        fetch('http://localhost:5000/coinpairs')
            .then((res) => res.json())
            .then((data) => {
                let coinpairs = data.coinpairs
                setData(coinpairs)
            })
        
        fetch('http://localhost:5000/watchlist')
        .then((res) => res.json())
        .then((data) => {
            setUserWatchlist(data)
        })
        // fetch('http://localhost:5000/alerts_notification')
        //     .then((res) => res.json())
        //     .then((data) => {
        //         setAlerts(data)
        //     })
    
        setLoading(false)
    }, [])


    useEffect(() =>{
        if (userWatchlist){
        let d = <div>
                {userWatchlist.coinpairs.map((coin) =>{return <Card coinpair_id={coin.coinpair_id}
                coinpair_sym={coin.coinpair_sym}
                price_update={coin.coinpair_price.insert_time}
                price_value={coin.coinpair_price.price}
                watchlisted={true}
                updateWatchlist={updateWatchlist}/>})}
        </div>
        setuser(d)
        // console.log(userWatchlist)
    }
    },[userWatchlist])



    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    return (
        <div>
            <div> Watchlist
                <div>
                    {/* {userWatchlist.coinpairs.map((coin) =>{return <Card coinpair_id={coin.coinpair_id}
                    coinpair_sym={coin.coinpair_sym}
                    price_update={coin.coinpair_price.insert_time}
                    price_value={coin.coinpair_price.price}
                    watchlisted={true}
                    watchlistState={setUserWatchlist}/>})}     */}
                    {user}
                </div>
            </div>
            ___________________________________________________
            <div id="Cards">
                {data.map((coin) =>{return <Card coinpair_id={coin.coinpair_id}
                    coinpair_sym={coin.coinpair_sym}
                    price_update={coin.coinpair_price.insert_time}
                    price_value={coin.coinpair_price.price}/>})}
            </div>
            <div id="modal-root"></div>
            <div>

            </div>

        </div>
    )
};
export default Homepage