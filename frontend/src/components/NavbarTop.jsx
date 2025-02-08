import {Navbar, NavbarBrand, NavbarContent, NavbarItem, Link, Button} from "@heroui/react";

export default function NavbarTop() {
  return (
    <Navbar shouldHideOnScroll>
      <NavbarBrand>
        <p style={{ color: "#25a100", fontSize: "20px"}} className="font-bold text-inherit">gromo</p>
      </NavbarBrand>
      <NavbarContent justify="end">
      <NavbarItem isActive>
          <Link style={{ color: "#60b048"}} href="#">
            Home
          </Link>
        </NavbarItem>
      <NavbarItem>
          <Link color="foreground" aria-current="page" href="#">
            Investment
          </Link>
        </NavbarItem>
        <NavbarItem>
          <Button as={Link} color="success" href="#" variant="flat">
            Login
          </Button>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
}
