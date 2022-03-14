function Card (props){
    return (
      <ul>
          <li>SYM: {props.coinpair_sym}</li>
          <li>Last Update: {props.price_update}</li>
          <li>Price: {props.price_value}</li>
      </ul>
  )
}
export default Card