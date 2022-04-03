import Card from "../comps/coinpairCard/Card.js";
import styles from "../styles/homeage.module.css"
const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {

    const [data, setData] = useState([])
    const [userWatchlist, setUserWatchlist] = useState([])
    const [watchlistCards, setWatchlistCards] = useState()
    const [coinpairCards, setCoinpairCards] = useState([])
    const [isLoading, setLoading] = useState(false)
    
    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>


    const updateWatchlist = (action,coinpairId) => {
        if (action=='remove') {
            let updated = userWatchlist.filter((e) => e.coinpair_id != coinpairId)        
            setUserWatchlist(updated)
          }
        else if (action=='add'){
            for (const coinpair of data) {
                if (coinpair.coinpair_id == coinpairId){
                    setUserWatchlist([...userWatchlist, coinpair])
                    break
                }
            }  
        }
    }

    //homepage cards get generated when we know the watchlist cards. To avoid duplicate cards in watchlist and homepage. 
    const homepageCards = () => {
        const watchlistCoinIDs = userWatchlist.map(coin => coin.coinpair_id)
        const cards = 
            <div id="Cards">
                {data.map((coin) =>{
                    if (!watchlistCoinIDs.includes(coin.coinpair_id)){
                        return <Card coinpair_id={coin.coinpair_id}
                        coinpair_sym={coin.coinpair_sym}
                        price_update={coin.coinpair_price.insert_time}
                        price_value={coin.coinpair_price.price}
                        watchlisted={false}
                        updateWatchlist={updateWatchlist}/>}
                        }
                    )
                }
            </div>
        setCoinpairCards(cards)
    }


    useEffect(() => {
        fetch('http://localhost:5000/coinpairs')
            .then((res) => res.json())
            .then((data) => {
                setData(data.coinpairs)
            })
        
        fetch('http://localhost:5000/watchlist')
        .then((res) => res.json())
        .then((data) => {
            setUserWatchlist(data.coinpairs)
        })
    
        
        setLoading(false)
    }, []);


    useEffect(() =>{
        if (userWatchlist.length != 0){
            let d = <div className={styles.watchlist}>
                        {userWatchlist.map((coin) =>{return <Card coinpair_id={coin.coinpair_id}
                            coinpair_sym={coin.coinpair_sym}
                            price_update={coin.coinpair_price.insert_time}
                            price_value={coin.coinpair_price.price}
                            watchlisted={true}
                            updateWatchlist={updateWatchlist}/>})}
                </div>
        setWatchlistCards(d)
        }
        homepageCards()
    },[userWatchlist])


    return (
        <div>
            <div> Watchlist
                    {watchlistCards}
            </div>
            ___________________________________________________
            <div> Coin Pairs
                {coinpairCards}
            </div>                
            <div id="modal-root"></div>
        </div>
    )
};
export default Homepage