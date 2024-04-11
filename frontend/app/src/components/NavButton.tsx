const NavButton: React.FC<any> = ({ name, redirect }) => {
  return (
    <button className="inline-block font-extralight text-2xl text-custom-blue py-3 border-2 border-custom-blue rounded-xl p-4 mt-6 uppercase hover:bg-custom-blue hover:text-custom-light-green active:bg-custom-teal active:text-custom-off-white">
      <a href={redirect} target="_blank" rel="noopener noreferrer">
        {name}
      </a>
    </button>
  );
};

export default NavButton;
