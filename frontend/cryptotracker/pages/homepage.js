import { API } from "../config";


import Card from "../comps/coinpairCard/Card.js";
import AlertCard from "../comps/alertCards/alertCards"
import styles from "../styles/homeage.module.css"
import { AlertCardType } from "../comps/alertCards/alertCards";

const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {
    const [data, setData] = useState([])
    const [userWatchlist, setUserWatchlist] = useState([])
    const [coinpairPage,setCoinpairPage] = useState(0)
    const [alerts,setAlerts] = useState([])
    
    const [watchlistCards, setWatchlistCards] = useState([])
    const [coinpairCards, setCoinpairCards] = useState([])
    const [generatedAlertsCards, setGeneratedAlertsCards] = useState([])
    const [alertCards, setAlertCards] = useState([])

    const [isLoading, setLoading] = useState(false)

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    //Onmount init api calls to get the coins, user watchlist, user's alerts, etc
    useEffect(() => {
        // fetch(`http://${API}/coinpairs`)
        //     .then((res) => res.json())
        //     .then((data) => {
        //         setData(data.coinpairs)   
        // });
        fetch(`http://${API}/watchlist`)
        .then((res) => res.json())
        .then((data) => {
            setUserWatchlist(data.coinpairs)
        });
        fetch(`http://${API}/alerts`)
        .then((res) => res.json())
        .then((data) => {
            setAlerts(data.alerts)
        });
        setLoading(false)
    }, []);

    //Called from the card component when a card is added/removed to update userWatchlist then watchlist cards rerenders 
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

    //Set the user watchlist cards, listening for changes to the userWatchlist so we can rerender the cards in watchlist section
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

    //Used to set the homeage cards, so when the data from the api call is complete we create the cards
    useEffect(() =>{
        homepageCards()
    },[data])

    //homepage cards get generated when we know the watchlist cards. To avoid duplicate cards in watchlist and homepage. 
    const homepageCards = () => {
        const watchlistCoinIDs = userWatchlist.map(coin => coin.coinpair_id)
        const cards = 
            <div id={styles.hompageCards} >
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

    const fetchCoinPair = async (coinpairId) => {
        const res = await fetch(`http://${API}/coinpair/${coinpairId}`)
        const json = await res.json()
        return json
    }

    //The paganation of the homepage cards so not all the coinpairs are loaded at once
    const fetchAdditionalCoins = () => {
        let nextPage = coinpairPage + 1
        setCoinpairPage(nextPage)
        fetch(`http://${API}/coinpairs?offset=${nextPage}`)
        .then((res) => res.json())
        .then((json) => {
            setData(data => data.concat([ ...json.coinpairs]) )  
    });
    }

    const createAlertCards = (alerts) => {
        console.log('Creating Information Alerts Cards')
        let t = []
        alerts.forEach(e => {
            let header = `Alert Type: ${e.alert_type}`
            fetchCoinPair(e.coin_pair_id).then(r => { 
                let body = [`Coin Pair SYM: ${r.coinpair_sym}`,`Threshold: ${e.threshold}`, `Threshold condition: ${e.threshold_condition}`]   
                let a = <AlertCard 
                            key={`${AlertCardType.INFO}:${e.alert_id}`}
                            cardHeader={header}
                            cardBody={body}
                            type={AlertCardType.INFO}
                            id={e.alert_id}/>
                            // alertData={e}
                            // coinInfo={1}  
                console.log(a)
                t.push(a)        
            })
        })
        setAlertCards(t)
        console.log('Finished Creating Information Alerts Cards')
    }

    const createGeneratedAlertCards = (alerts) => {
        console.log('Creating Generated Alert Cards')
        let html = alerts.map(e => {
            let header = `${e.alert_type} triggered`
            //Todo: Fix this as alert can have multiple generations
            let body = [`${e.generation_history[0].msg}`]
            return <AlertCard 
                    key={`${AlertCardType.GENERATION}:${e.generation_history[0]._id}`}
                    cardHeader={header}
                    cardBody={body} 
                    type={AlertCardType.GENERATION} 
                    id={e.generation_history[0]._id}/>
        })
        setGeneratedAlertsCards(html)
        console.log('Finished Creating Generated Alert Cards')
    }

    //Get alerts that have been generated
    useEffect(() => {
        if (alerts.length == 0) {return}
        const genAlerts = alerts.filter(genAlert => {
            const genHistory = genAlert.generation_history
            if (genHistory.length > 0) 
                return genAlert
        })
        createAlertCards(alerts)    
        createGeneratedAlertCards(genAlerts)
            
    },[alerts])


    return (
        <div>
            <div style={{display:'flex',flexDirection:'row'}}>
                <div style={{width:'80%'}}>
                    <div> Watchlist
                            {watchlistCards}
                    </div>
                    ___________________________________________________
                    <div> Coin Pairs
                        {coinpairCards}
                    </div>
                </div>
                <div style={{width:'20%'}}>
                <div> Triggered alerts
                        {generatedAlertsCards.map(e=>e)}
                    </div>
                    <div> My Alerts
                        {alertCards.map(e=>{;
                        return e})}
                    </div>
                </div>
            </div>
            <div>
                <div onClick={fetchAdditionalCoins}>
                    load more
                </div>
            </div>
            <div id="modal-root"></div>
        </div>
    )
};
export default Homepage