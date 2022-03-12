function Blog({ posts }) {
  const coin = get_coins()
  console.log(coin)
  return (
    <ul>
      hi

    </ul>
  )
}
async function get_coins(){
  const res = await fetch('http://192.168.1.31:5000/coinpair/61f5814d32e2534f6e8e0ef7')
  const posts = await res.json()
  console.log(posts)
}
// // This function gets called at build time
// export async function getStaticProps() {
//   // Call an external API endpoint to get posts
//   const res = await fetch('http://192.168.1.31:5000/coinpairs')
//   const posts = await res.json()
//   console.log(posts)
//   // By returning { props: { posts } }, the Blog component
//   // will receive `posts` as a prop at build time
//   return {
//     props: {
//       posts,
//     },
//   }
// }

export default Blog
